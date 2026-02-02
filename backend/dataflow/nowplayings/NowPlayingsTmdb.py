from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
from datetime import date
import requests


class NowPlayingsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "allShowtimes"
    MOVING_TO_TABLE_NAME = "finalShowtimes"
    MOVING_TO_TABLE_NAME_2 = "finalMovies"
    HELPER_TABLE_NAME = "tableFixes"
    HELPER_TABLE_NAME_2 = "tableSkips"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME_2)

        for skip_row in self.helper_table_2_rows:
            skip_value = skip_row.get("name_or_tmdb_id").strip()
            self.skip_tokens.add(skip_value.lower())
            self.skip_tokens.add(self.normalizeTitle(skip_value).strip().lower())

        for fix in self.helper_table_rows:
            tmdb_id = fix.get("tmdb_id").strip()
            title_fix = fix.get("title_fix").strip().lower()
            if not tmdb_id or not title_fix:
                continue
            tmdb_id = int(tmdb_id)
            self.tmdb_fix_ids.add(tmdb_id)
            self.tmdb_fix_by_title[title_fix] = tmdb_id
            self.tryExceptPass(lambda: self.tmdb_fix_by_title.__setitem__(self.normalizeTitle(title_fix).strip().lower(), tmdb_id))

        for row in self.main_table_rows:
            self.reset_np_main_row_state()
            self.load_np_main_row(row)
            if row.get("added") or (self.date_of_showing and self.dateToDate(self.date_of_showing) < date.today()):
                continue

            title_norm = self.normalizeTitle(self.english_title)
            key = self.nowPlayingsGroupKey(title_norm)
            if not (title_norm and key):
                continue

            self.grouped_rows_by_key[key].append(row)
            self.title_counts_by_key[key][title_norm] += 1

            meta = self.meta_by_key.setdefault(key, {"hebrew_title": self.hebrew_title, "directed_by": self.directed_by, "runtime": self.runtime, "year_counts": defaultdict(int)})
            meta["hebrew_title"] = meta.get("hebrew_title") if meta.get("hebrew_title") or not self.hebrew_title else self.hebrew_title
            meta["directed_by"] = meta.get("directed_by") if meta.get("directed_by") or not self.directed_by else self.directed_by
            meta["runtime"] = meta.get("runtime") if meta.get("runtime") or not self.runtime else self.runtime

            self.release_year is not None and self.tryExceptPass(lambda: meta["year_counts"].__setitem__(self.release_year, meta["year_counts"].get(self.release_year, 0) + 1))

        for key, rows in self.grouped_rows_by_key.items():
            self.reset_np_groupkey_row_state()
            meta = self.meta_by_key.get(key) or {}
            hebrew_title, directed_by, runtime, year_counts, parsed_year = meta.get("hebrew_title"), meta.get("directed_by"), meta.get("runtime"), meta.get("year_counts") or {}, None

            if year_counts:
                parsed_year = self.tryExceptNone(lambda: max(year_counts.items(), key=lambda kv: kv[1])[0])

            title_counts = self.title_counts_by_key.get(key) or {}
            titles_sorted = sorted(title_counts.items(), key=lambda kv: kv[1], reverse=True)
            candidate_titles = [title for title, _ in titles_sorted if not self.titleIsSkipped(title, self.skip_tokens)]
            if not candidate_titles:
                continue
            representative_title = candidate_titles[0]

            # TMDB FIX OVERRIDE (title -> tmdb_id)
            for title in candidate_titles:
                title_raw = (title or "").strip().lower()
                try:
                    title_norm = self.normalizeTitle(title or "").strip().lower()
                except:
                    title_norm = title_raw
                self.override_tmdb = self.tmdb_fix_by_title.get(title_raw) or self.tmdb_fix_by_title.get(title_norm)
                if self.override_tmdb:
                    break
            if self.override_tmdb:
                self.potential_chosen_id = self.override_tmdb
                if str(self.potential_chosen_id).lower() in self.skip_tokens:
                    continue
                self.key_result[key] = {"tmdb_id": self.potential_chosen_id, "imdb_id": None, "hebrew_title": hebrew_title}
                continue

            # 1) SEARCH TMDB AND COLLECT CANDIDATES
            if parsed_year:
                self.search_plans += [(24, 8, year) for year in (parsed_year, parsed_year - 1, parsed_year + 1)]
            self.search_plans.append((20, None, None))
            for max_total, max_plan, year in self.search_plans:
                if len(self.candidates) >= max_total:
                    continue

                added, page = 0, 1
                while len(self.candidates) < max_total and (max_plan is None or added < max_plan):
                    params = {"api_key": self.TMDB_API_KEY, "query": representative_title, "page": page}
                    if year is not None:
                        params["primary_release_year"] = year
                    try:
                        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=10).json()
                    except:
                        break
                    results = response.get("results") or []
                    if not results:
                        break

                    for movie_result in results:
                        if not (tmdb_id := movie_result.get("id")) or tmdb_id in self.seen_already:
                            continue
                        self.seen_already.add(tmdb_id)
                        self.candidates.append(tmdb_id)
                        added += 1
                        if len(self.candidates) >= max_total or (max_plan is not None and added >= max_plan):
                            break
                    page += 1

            if not self.candidates:
                continue

            # 2) FETCH FULL DETAILS (external_ids + credits)
            for tmdb_id in self.candidates:
                self.tryExceptPass(lambda: (resp := requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids,credits"}, timeout=10).json()) and resp.get("id") and self.details.update({tmdb_id: resp}))
            if not self.details:
                continue

            # 3) TMDb FIX TABLE HARD MATCH (fast set membership)
            for tmdb_id in self.details.keys():
                if tmdb_id in self.tmdb_fix_ids:
                    self.potential_chosen_id = tmdb_id
                    break

            # 4) FALLBACK FIRST/DIRECTOR/RUNTIME RANKING LOGIC
            if self.potential_chosen_id is None:
                first = self.details.get(self.candidates[0])
                if first and (self.normalizeTitle(first.get("title")) == self.normalizeTitle(representative_title)) and (not parsed_year or self.tryExceptNone(lambda: int((first.get("release_date") or "")[:4]) == parsed_year)):
                    self.potential_chosen_id = self.candidates[0]

                if self.potential_chosen_id is None and directed_by:
                    target = str(directed_by).lower()
                    for tmdb_id, movie_details in self.details.items():
                        crew = movie_details.get("credits", {}).get("crew", [])
                        directors = [crew_member["name"].lower() for crew_member in crew if crew_member.get("job") == "Director" and crew_member.get("name")]
                        if target in directors:
                            self.potential_chosen_id = tmdb_id
                            break

                if self.potential_chosen_id is None and runtime and hasattr(self, "fake_runtimes") and runtime not in self.fake_runtimes:
                    for tmdb_id, movie_details in self.details.items():
                        if movie_details.get("runtime") == runtime:
                            self.potential_chosen_id = tmdb_id
                            break

                if self.potential_chosen_id is None:
                    self.potential_chosen_id = self.candidates[0]

            if not self.potential_chosen_id or str(self.potential_chosen_id).lower() in self.skip_tokens:
                continue

            chosen_details = self.details.get(self.potential_chosen_id) or {}
            chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            self.key_result[key] = {"tmdb_id": self.potential_chosen_id, "imdb_id": chosen_imdb, "hebrew_title": hebrew_title}

        # 5) DEDUPE BY TMDB ID
        for key, res in self.key_result.items():
            if (tmdb_id := res.get("tmdb_id")) and tmdb_id not in self.movies_by_tmdb:
                self.movies_by_tmdb[tmdb_id] = res

        # 6) ENRICH TITLE + POSTER (+ imdb_id)
        for tmdb_id, res in self.movies_by_tmdb.items():
            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}, timeout=10).json()
            except:
                continue
            if not isinstance(data, dict) or not data.get("id"):
                continue
            external_ids = data.get("external_ids") or {}

            res["english_title"] = data["title"].strip() if data.get("title") else res.get("english_title")
            res["runtime"] = data["runtime"] if data.get("runtime") is not None else res.get("runtime")
            res["popularity"] = data["popularity"] if data.get("popularity") is not None else res.get("popularity")
            res["imdb_id"] = external_ids.get("imdb_id") or res.get("imdb_id")
            res["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else res.get("poster")
            res["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"] if data.get("backdrop_path") else res.get("backdrop")
            res["year"] = data["release_date"][:4] if data.get("release_date") else res.get("year")

        tmdb_id_to_enriched = dict(self.movies_by_tmdb)
        for key, rows in self.grouped_rows_by_key.items():
            group_res = self.key_result.get(key)
            tmdb_id = (group_res or {}).get("tmdb_id")
            enriched = tmdb_id_to_enriched.get(tmdb_id) if tmdb_id else None
            final_title = (enriched or {}).get("english_title") if enriched else None

            for row in rows:
                if not tmdb_id or self.titleIsSkipped(self.normalizeTitle(row.get("english_title")), self.skip_tokens):
                    continue

                new_row = dict(row)
                new_row["tmdb_id"] = tmdb_id
                new_row["english_title"] = final_title if final_title else self.normalizeTitle(row.get("english_title"))

                for column in ("added", "cleaned", "release_year", "rating", "directed_by", "runtime"):
                    new_row.pop(column, None)

                self.processed_ids.add(row["id"])
                self.updates.append(new_row)

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
        if self.processed_ids:
            ids = list(self.processed_ids)
            for i in range(0, len(ids), 200):
                chunk = ids[i : i + 200]
                self.supabase.table(self.MAIN_TABLE_NAME).update({"added": True}).in_("id", chunk).execute()
        self.dedupeTable(self.MOVING_TO_TABLE_NAME, ignore_cols={"id", "created_at", "run_id", "release_year", "hebrew_title", "hebrew_href", "english_href", "rating", "directed_by", "runtime"}, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)

        for tmdb_id, res in tmdb_id_to_enriched.items():
            if not tmdb_id:
                continue
            imdb_id = res.get("imdb_id") or None
            self.updates.append({"tmdb_id": tmdb_id, "english_title": res.get("english_title"), "runtime": res.get("runtime"), "popularity": res.get("popularity"), "imdb_id": imdb_id, "poster": res.get("poster"), "backdrop": res.get("backdrop"), "year": res.get("year")})

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME_2)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME_2, ignore_cols={"english_title", "runtime", "popularity", "poster", "backdrop", "imdb_id", "imdbRating", "imdbVotes", "rtRating", "year"}, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)
