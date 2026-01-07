from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
from datetime import date
import requests


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    MOVING_TO_TABLE_NAME = "testingFinalSoons"
    HELPER_TABLE_NAME = "testingFixes"
    HELPER_TABLE_NAME_2 = "testingSkips"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME)

        # BUILD SKIP LOOKUP
        skip_tokens = set()
        for skip_row in self.helper_table_2_rows:
            skip_value = skip_row.get("name_or_tmdb_id").strip()
            if not skip_value:
                continue
            skip_tokens.add(skip_value.lower())

            try:
                skip_tokens.add(self.normalizeTitle(skip_value).strip().lower())
            except:
                pass

        # BUILD TMDb FIX LOOKUPS
        tmdb_fix_ids, tmdb_fix_by_title = set(), {}
        for fix in self.helper_table_rows:
            tmdb_id = fix.get("tmdb_id").strip()
            title_fix = fix.get("title_fix").strip().lower()
            if not tmdb_id or not title_fix:
                continue
            tmdb_id = int(tmdb_id)
            tmdb_fix_ids.add(tmdb_id)
            tmdb_fix_by_title[title_fix] = tmdb_id
            try:
                tmdb_fix_by_title[self.normalizeTitle(title_fix).strip().lower()] = tmdb_id
            except:
                pass

        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            if self.release_date and self.dateToDate(self.release_date) < date.today():
                continue

            original_uuid = row.get("id")
            original_run_id = row.get("run_id")
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

            # TMDB FIX OVERRIDE
            override_tmdb = tmdb_fix_by_title.get(title_raw) or tmdb_fix_by_title.get(title_norm)
            if override_tmdb:
                self.potential_chosen_id = override_tmdb
                if str(self.potential_chosen_id).lower() in skip_tokens:
                    continue
                self.non_deduplicated_updates.append({"old_uuid": original_uuid, "run_id": original_run_id, "english_title": original_title, "hebrew_title": self.hebrew_title, "release_date": original_release_date, "tmdb_id": self.potential_chosen_id, "imdb_id": None})
                continue

            # 1) SEARCH TMDB AND COLLECT CANDIDATES
            seen = set()
            if not self.release_year:
                page = 1
                while len(self.candidates) < 20:
                    params = {"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": page}
                    try:
                        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params).json()
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
                        self.candidates.append(tmdb_id)
                        if len(self.candidates) >= 20:
                            break

                    page += 1

            else:
                for year in [int(self.release_year), int(self.release_year) - 1, int(self.release_year) + 1]:
                    if len(self.candidates) >= 24:
                        break

                    added_this_year, page = 0, 1
                    while len(self.candidates) < 24 and added_this_year < 8:
                        params = {"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": page, "primary_release_year": year}

                        try:
                            response = requests.get("https://api.themoviedb.org/3/search/movie", params=params).json()
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
                            self.candidates.append(tmdb_id)
                            added_this_year += 1

                            if len(self.candidates) >= 24 or added_this_year >= 8:
                                break
                        page += 1

                page = 1
                while len(self.candidates) < 20:
                    params = {"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": page}
                    try:
                        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params).json()
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
                        self.candidates.append(tmdb_id)

                        if len(self.candidates) >= 20:
                            break

                    page += 1

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

            # 3) TMDb FIX TABLE HARD MATCH (fast set membership)
            for tmdb_id, movie_details in self.details.items():
                if int(tmdb_id) in tmdb_fix_ids:
                    self.potential_chosen_id = int(tmdb_id)
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
            if not self.potential_chosen_id or str(self.potential_chosen_id).lower() in skip_tokens:
                continue

            chosen_details = self.details.get(self.potential_chosen_id) or {}
            chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            self.non_deduplicated_updates.append({"old_uuid": original_uuid, "run_id": original_run_id, "english_title": original_title, "hebrew_title": self.hebrew_title, "release_date": original_release_date, "tmdb_id": self.potential_chosen_id, "imdb_id": chosen_imdb})

        # 5) DEDUPE BY TMDB ID
        grouped = defaultdict(list)
        for row in self.non_deduplicated_updates:
            tmdb_id = row.get("tmdb_id")
            if tmdb_id:
                grouped[tmdb_id].append(row)

        for tmdb_id, rows in grouped.items():
            rows_sorted = sorted(rows, key=self.comingSoonsFinalDedupeSortKey)
            best = rows_sorted[0]

            if (best.get("hebrew_title") or "").strip() in ("", "null"):
                for candidate_row in rows_sorted:
                    hebrew_title = (candidate_row.get("hebrew_title") or "").strip()
                    if hebrew_title not in ("", "null"):
                        best["hebrew_title"] = hebrew_title
                        break

            self.non_enriched_updates.append(best)

        # 6) ENRICH TITLE + POSTER + IMDB_ID
        for row in self.non_enriched_updates:
            tmdb_id = row.get("tmdb_id")
            if not tmdb_id:
                continue

            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}).json()
            except:
                continue

            new_row = dict(row)

            if data.get("title"):
                new_row["english_title"] = data["title"].strip()

            external_ids = data.get("external_ids") or {}
            imdb_id = external_ids.get("imdb_id")
            if imdb_id:
                new_row["imdb_id"] = imdb_id

            if data.get("poster_path"):
                new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("backdrop_path"):
                new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"]

            self.updates.append(new_row)

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME, ignore_cols={"poster", "backdrop", "release_date", "hebrew_title"}, sort_key=self.comingSoonsFinalDedupeSortKey2)
