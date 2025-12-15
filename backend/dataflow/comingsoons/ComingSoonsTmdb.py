from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests

from backend.dataflow.comingsoons.supabaseHelpers.clear.testingSoons import clear_testingSoons
from backend.dataflow.comingsoons.supabaseHelpers.clear.testingFinalSoons import clear_testingFinalSoons
from backend.dataflow.comingsoons.supabaseHelpers.append.finalSoonstoFinalSoons2 import append_testingFinalSoons_to_testingFinalSoons2


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    MOVING_TO_TABLE_NAME = "testingFinalSoons"
    MOVING_TO_TABLE_NAME_2 = "testingFinalSoons2"
    HELPER_TABLE_NAME = "testingIMDbFixes"
    HELPER_TABLE_NAME_2 = "testingSkips"

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

        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            original_title = self.english_title
            original_release_date = self.release_date

            # SKIP TITLES
            title_raw = (self.english_title or "").strip().lower()
            try:
                title_norm = self.normalizeTitle(self.english_title or "").strip().lower()
            except:
                title_norm = title_raw

            if title_raw in skip_tokens or title_norm in skip_tokens:
                continue

            # IMDB FIX OVERRIDE
            override_imdb = imdb_fix_by_title.get(title_raw) or imdb_fix_by_title.get(title_norm)
            if override_imdb:
                try:
                    find_data = requests.get(f"https://api.themoviedb.org/3/find/{override_imdb}", params={"api_key": self.TMDB_API_KEY, "external_source": "imdb_id"}).json()
                except:
                    find_data = None

                movie_results = (find_data or {}).get("movie_results") or []
                if movie_results and movie_results[0].get("id"):
                    self.potential_chosen_id = movie_results[0]["id"]
                    self.non_deduplicated_updates.append({"english_title": original_title, "hebrew_title": self.hebrew_title, "release_date": original_release_date, "tmdb_id": self.potential_chosen_id, "imdb_id": override_imdb})
                    continue

            # 1) SEARCH TMDB AND COLLECT FIRST ~15 RESULTS
            while len(self.candidates) < 15:
                try:
                    response = requests.get("https://api.themoviedb.org/3/search/movie", params={"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": self.results_page}).json()
                except:
                    break

                results = response.get("results") or []
                if not results:
                    break

                for movie_result in results:
                    tmdb_id = movie_result.get("id")
                    if tmdb_id:
                        self.candidates.append(tmdb_id)
                    if len(self.candidates) == 15:
                        break
                self.results_page += 1
            if not self.candidates:
                continue

            # 2) FETCH FULL DETAILS (external_ids + credits)
            for tmdb_id in self.candidates:
                try:
                    movie_response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids,credits"}).json()
                    if movie_response.get("id"):
                        self.details[tmdb_id] = movie_response
                except:
                    pass

            if not self.details:
                continue

            # 3) IMDb FIX TABLE HARD MATCH (fast set membership)
            for tmdb_id, movie_details in self.details.items():
                imdb_id = (movie_details.get("external_ids", {}) or {}).get("imdb_id")
                if imdb_id and imdb_id in imdb_fix_ids:
                    self.potential_chosen_id = tmdb_id
                    break

            # 4) FALLBACK FIRST/DIRECTOR/RUNTIME RANKING LOGIC
            if self.potential_chosen_id is None:
                first = self.details.get(self.candidates[0])
                if first:
                    first_title = first.get("title") or ""
                    try:
                        title_match = self.normalizeTitle(first_title).strip().lower() == self.normalizeTitle(str(self.english_title)).strip().lower()
                    except:
                        title_match = (first_title or "").strip().lower() == (self.english_title or "").strip().lower()

                    if self.release_year and first.get("release_date"):
                        try:
                            self.found_year_match = int(first["release_date"][:4]) == self.release_year
                        except:
                            pass

                    if title_match and self.found_year_match:
                        self.potential_chosen_id = self.candidates[0]

                # Director match
                if self.potential_chosen_id is None and self.directed_by:
                    target = self.directed_by.lower()
                    for tmdb_id, movie_details in self.details.items():
                        crew = movie_details.get("credits", {}).get("crew", [])
                        directors = [crew_member["name"].lower() for crew_member in crew if crew_member.get("job") == "Director" and crew_member.get("name")]
                        if target in directors:
                            self.potential_chosen_id = tmdb_id
                            break

                # Runtime match
                if self.potential_chosen_id is None and self.runtime and self.runtime not in self.fake_runtimes:
                    for tmdb_id, movie_details in self.details.items():
                        if movie_details.get("runtime") == self.runtime:
                            self.potential_chosen_id = tmdb_id
                            break

                if self.potential_chosen_id is None:
                    self.potential_chosen_id = self.candidates[0]
            if not self.potential_chosen_id:
                continue

            chosen_details = self.details.get(self.potential_chosen_id) or {}
            chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            self.non_deduplicated_updates.append({"english_title": original_title, "hebrew_title": self.hebrew_title, "release_date": original_release_date, "tmdb_id": self.potential_chosen_id, "imdb_id": chosen_imdb})

        # 5) DEDUPE BY IMDB ID
        grouped = defaultdict(list)
        for row in self.non_deduplicated_updates:
            imdb_id = row.get("imdb_id")
            if imdb_id:
                grouped[imdb_id].append(row)

        for imdb_id, rows in grouped.items():
            rows_sorted = sorted(rows, key=self.comingSoonsFinalDedupeSortKey)
            best = rows_sorted[0]

            if (best.get("hebrew_title") or "").strip() in ("", "null"):
                for candidate_row in rows_sorted:
                    hebrew_title = (candidate_row.get("hebrew_title") or "").strip()
                    if hebrew_title not in ("", "null"):
                        best["hebrew_title"] = hebrew_title
                        break
            self.non_enriched_updates.append(best)

        # 6) ENRICH TITLE + POSTER
        for row in self.non_enriched_updates:
            tmdb_id = row.get("tmdb_id")
            if not tmdb_id:
                continue

            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY}).json()
            except:
                continue

            new_row = dict(row)
            if data.get("title"):
                new_row["english_title"] = data["title"].strip()
            if data.get("poster_path"):
                new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("backdrop_path"):
                new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"]
            self.updates.append(new_row)

        clear_testingFinalSoons()
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
        append_testingFinalSoons_to_testingFinalSoons2()
        clear_testingSoons()
