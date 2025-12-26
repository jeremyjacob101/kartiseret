from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests

from backend.dataflow.nowplayings.supabaseHelpers.append.finalMoviestofinalMovies2 import append_testingFinalMovies_to_testingFinalMovies2
from backend.dataflow.nowplayings.supabaseHelpers.append.finalShowtimestofinalShowtimes2 import append_testingFinalShowtimes_to_testingFinalShowtimes2
from backend.dataflow.nowplayings.supabaseHelpers.append.showtimestoshowtimes2 import append_testingShowtimes_to_testingShowtimes2
from backend.dataflow.nowplayings.supabaseHelpers.clear.testingFinalShowtimes import clear_testingFinalShowtimes
from backend.dataflow.nowplayings.supabaseHelpers.clear.testingFinalMovies import clear_testingFinalMovies
from backend.dataflow.nowplayings.supabaseHelpers.clear.testingShowtimes import clear_testingShowtimes


class NowPlayingsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingShowtimes"
    MOVING_TO_TABLE_NAME = "testingFinalShowtimes"
    MOVING_TO_TABLE_NAME_2 = "testingFinalMovies"
    HELPER_TABLE_NAME = "testingIMDbFixes"
    HELPER_TABLE_NAME_2 = "testingSkips"
    HELPER_TABLE_NAME_3 = "testingFinalShowtimes2"
    HELPER_TABLE_NAME_4 = "testingFinalMovies2"

    def nowPlayingsGroupKey(self, normalized_title: str) -> str:
        t = (normalized_title or "").strip().lower()
        for prefix in ("the ", "a ", "an "):
            if t.startswith(prefix):
                t = t[len(prefix) :].strip()
                break
        return t

    def titleIsSkipped(self, title: str, skip_tokens: set) -> bool:
        title_raw = (title or "").strip().lower()
        try:
            title_norm = self.normalizeTitle(title or "").strip().lower()
        except:
            title_norm = title_raw
        return title_raw in skip_tokens or title_norm in skip_tokens

    def logic(self):
        # BUILD SKIP LOOKUP (testingSkips)
        skip_tokens = set()
        for skip_row in self.helper_table_2_rows:
            skip_value = (skip_row.get("name_or_imdb_id") or skip_row.get("id") or "").strip()
            if not skip_value:
                continue
            skip_tokens.add(skip_value.lower())

            try:
                skip_tokens.add(self.normalizeTitle(skip_value).strip().lower())
            except:
                pass

        # BUILD IMDb FIX LOOKUPS (testingIMDbFixes)
        imdb_fix_ids = set()
        imdb_fix_by_title = {}

        for fix in self.helper_table_rows:
            imdb_id = (fix.get("imdb_id") or "").strip()
            title_fix = (fix.get("title_fix") or "").strip()
            if not imdb_id or not title_fix:
                continue

            imdb_fix_ids.add(imdb_id)

            title_low = title_fix.lower()
            imdb_fix_by_title[title_low] = imdb_id
            try:
                imdb_fix_by_title[self.normalizeTitle(title_fix).strip().lower()] = imdb_id
            except:
                pass

        grouped_rows_by_key = defaultdict(list)
        title_counts_by_key = defaultdict(lambda: defaultdict(int))
        meta_by_key = {}

        for row in self.main_table_rows:
            title_norm = self.normalizeTitle(row.get("english_title") or "").strip()
            if not title_norm:
                continue

            key = self.nowPlayingsGroupKey(title_norm)
            if not key:
                continue

            grouped_rows_by_key[key].append(row)
            title_counts_by_key[key][title_norm] += 1

            meta = meta_by_key.get(key)
            if meta is None:
                meta_by_key[key] = {
                    "hebrew_title": row.get("hebrew_title"),
                    "directed_by": row.get("directed_by"),
                    "runtime": row.get("runtime"),
                    "year_counts": defaultdict(int),
                }
                meta = meta_by_key[key]

            if not meta.get("hebrew_title") and row.get("hebrew_title"):
                meta["hebrew_title"] = row.get("hebrew_title")
            if not meta.get("directed_by") and row.get("directed_by"):
                meta["directed_by"] = row.get("directed_by")
            if not meta.get("runtime") and row.get("runtime"):
                meta["runtime"] = row.get("runtime")

            ry = row.get("release_year")
            try:
                if ry not in ("", "null", None):
                    meta["year_counts"][int(ry)] += 1
            except:
                pass

        key_result = {}
        tmdb_basic_cache = {}

        for key, rows in grouped_rows_by_key.items():
            meta = meta_by_key.get(key) or {}

            hebrew_title = meta.get("hebrew_title")
            directed_by = meta.get("directed_by")
            runtime = meta.get("runtime")

            year_counts = meta.get("year_counts") or {}
            parsed_year = None
            if year_counts:
                try:
                    parsed_year = max(year_counts.items(), key=lambda kv: kv[1])[0]
                except:
                    parsed_year = None

            title_counts = title_counts_by_key.get(key) or {}
            titles_sorted = sorted(title_counts.items(), key=lambda kv: kv[1], reverse=True)
            candidate_titles = [t for t, _ in titles_sorted if not self.titleIsSkipped(t, skip_tokens)]
            if not candidate_titles:
                continue

            potential_chosen_id = None
            candidates = []
            details = {}

            # IMDB FIX OVERRIDE
            override_imdb = None
            for t in candidate_titles:
                t_raw = (t or "").strip().lower()
                try:
                    t_norm = self.normalizeTitle(t or "").strip().lower()
                except:
                    t_norm = t_raw
                override_imdb = imdb_fix_by_title.get(t_raw) or imdb_fix_by_title.get(t_norm)
                if override_imdb:
                    break

            if override_imdb:
                try:
                    find_data = requests.get(
                        f"https://api.themoviedb.org/3/find/{override_imdb}",
                        params={"api_key": self.TMDB_API_KEY, "external_source": "imdb_id"},
                        timeout=20,
                    ).json()
                except:
                    find_data = None

                movie_results = (find_data or {}).get("movie_results") or []
                if movie_results and movie_results[0].get("id"):
                    potential_chosen_id = movie_results[0]["id"]
                    key_result[key] = {"tmdb_id": potential_chosen_id, "imdb_id": override_imdb, "hebrew_title": hebrew_title}
                    continue

            representative_title = candidate_titles[0]

            # 1) SEARCH TMDB AND COLLECT CANDIDATES
            seen = set()

            if not parsed_year:
                page = 1
                while len(candidates) < 20:
                    params = {"api_key": self.TMDB_API_KEY, "query": representative_title, "page": page}
                    try:
                        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=20).json()
                    except:
                        break

                    results = response.get("results") or []
                    if not results:
                        break

                    for movie_result in results:
                        tmdb_id = movie_result.get("id")
                        if not tmdb_id or tmdb_id in seen:
                            continue
                        seen.add(tmdb_id)
                        candidates.append(tmdb_id)
                        if len(candidates) >= 20:
                            break

                    page += 1

            else:
                for year in [parsed_year, parsed_year - 1, parsed_year + 1]:
                    if len(candidates) >= 24:
                        break

                    added_this_year, page = 0, 1
                    while len(candidates) < 24 and added_this_year < 8:
                        params = {"api_key": self.TMDB_API_KEY, "query": representative_title, "page": page, "primary_release_year": year}

                        try:
                            response = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=20).json()
                        except:
                            break

                        results = response.get("results") or []
                        if not results:
                            break

                        for movie_result in results:
                            tmdb_id = movie_result.get("id")
                            if not tmdb_id or tmdb_id in seen:
                                continue
                            seen.add(tmdb_id)
                            candidates.append(tmdb_id)
                            added_this_year += 1

                            if len(candidates) >= 24 or added_this_year >= 8:
                                break
                        page += 1

                page = 1
                while len(candidates) < 30:
                    params = {"api_key": self.TMDB_API_KEY, "query": representative_title, "page": page}
                    try:
                        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=20).json()
                    except:
                        break

                    results = response.get("results") or []
                    if not results:
                        break

                    for movie_result in results:
                        tmdb_id = movie_result.get("id")
                        if not tmdb_id or tmdb_id in seen:
                            continue
                        seen.add(tmdb_id)
                        candidates.append(tmdb_id)

                        if len(candidates) >= 30:
                            break

                    page += 1

            if not candidates:
                continue

            # 2) FETCH FULL DETAILS (external_ids + credits)
            for tmdb_id in candidates:
                try:
                    movie_response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids,credits"}, timeout=20).json()
                    if movie_response.get("id"):
                        details[tmdb_id] = movie_response
                except:
                    pass

            if not details:
                continue

            # 3) IMDb FIX TABLE HARD MATCH (fast set membership)
            for tmdb_id, movie_details in details.items():
                imdb_id = (movie_details.get("external_ids", {}) or {}).get("imdb_id")
                if imdb_id and imdb_id in imdb_fix_ids:
                    potential_chosen_id = tmdb_id
                    break

            # 4) FALLBACK FIRST/DIRECTOR/RUNTIME RANKING LOGIC
            if potential_chosen_id is None:
                first = details.get(candidates[0])
                if first:
                    first_title = first.get("title") or ""
                    try:
                        title_match = self.normalizeTitle(first_title).strip().lower() == self.normalizeTitle(str(representative_title)).strip().lower()
                    except:
                        title_match = (first_title or "").strip().lower() == (representative_title or "").strip().lower()

                    found_year_match = False
                    if parsed_year and first.get("release_date"):
                        try:
                            found_year_match = int(first["release_date"][:4]) == parsed_year
                        except:
                            pass

                    if title_match and (not parsed_year or found_year_match):
                        potential_chosen_id = candidates[0]

                if potential_chosen_id is None and directed_by:
                    target = str(directed_by).lower()
                    for tmdb_id, movie_details in details.items():
                        crew = movie_details.get("credits", {}).get("crew", [])
                        directors = [crew_member["name"].lower() for crew_member in crew if crew_member.get("job") == "Director" and crew_member.get("name")]
                        if target in directors:
                            potential_chosen_id = tmdb_id
                            break

                if potential_chosen_id is None and runtime and hasattr(self, "fake_runtimes") and runtime not in self.fake_runtimes:
                    for tmdb_id, movie_details in details.items():
                        if movie_details.get("runtime") == runtime:
                            potential_chosen_id = tmdb_id
                            break

                if potential_chosen_id is None:
                    potential_chosen_id = candidates[0]

            if not potential_chosen_id:
                continue

            chosen_details = details.get(potential_chosen_id) or {}
            chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            key_result[key] = {"tmdb_id": potential_chosen_id, "imdb_id": chosen_imdb, "hebrew_title": hebrew_title}

        # 5) DEDUPE BY TMDB ID
        movies_by_tmdb = {}
        for key, res in key_result.items():
            tmdb_id = res.get("tmdb_id")
            if not tmdb_id:
                continue
            if tmdb_id not in movies_by_tmdb:
                movies_by_tmdb[tmdb_id] = res

        # 6) ENRICH TITLE + POSTER
        for tmdb_id, res in list(movies_by_tmdb.items()):
            if tmdb_id not in tmdb_basic_cache:
                try:
                    tmdb_basic_cache[tmdb_id] = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY}, timeout=20).json()
                except:
                    tmdb_basic_cache[tmdb_id] = {}

            data = tmdb_basic_cache.get(tmdb_id) or {}
            if data.get("title"):
                res["english_title"] = data["title"].strip()
            if data.get("runtime"):
                res["runtime"] = data["runtime"]
            if data.get("popularity"):
                res["popularity"] = data["popularity"]
            if data.get("poster_path"):
                res["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("backdrop_path"):
                res["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"]

        tmdb_id_to_enriched = dict(movies_by_tmdb)

        for key, rows in grouped_rows_by_key.items():
            group_res = key_result.get(key)
            tmdb_id = (group_res or {}).get("tmdb_id")
            enriched = tmdb_id_to_enriched.get(tmdb_id) if tmdb_id else None
            final_title = (enriched or {}).get("english_title") if enriched else None

            for row in rows:
                if not tmdb_id or self.titleIsSkipped(self.normalizeTitle(row.get("english_title")), skip_tokens):
                    continue

                new_row = dict(row)
                new_row["tmdb_id"] = tmdb_id
                if final_title:
                    new_row["english_title"] = final_title
                else:
                    new_row["english_title"] = self.normalizeTitle(row.get("english_title"))

                self.updates.append(new_row)

        append_testingFinalShowtimes_to_testingFinalShowtimes2()
        clear_testingFinalShowtimes()
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)

        for tmdb_id, res in tmdb_id_to_enriched.items():
            if not tmdb_id:
                continue
            self.updates.append({"tmdb_id": tmdb_id, "english_title": res.get("english_title"), "runtime": res.get("runtime"), "popularity": res.get("popularity"), "poster": res.get("poster"), "backdrop": res.get("backdrop")})

        append_testingFinalMovies_to_testingFinalMovies2()
        clear_testingFinalMovies()
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME_2)

        append_testingShowtimes_to_testingShowtimes2()
        clear_testingShowtimes()
