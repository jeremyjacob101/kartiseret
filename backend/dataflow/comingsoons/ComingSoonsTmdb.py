from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
from datetime import date
import requests


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "allSoons"
    MOVING_TO_TABLE_NAME = "finalSoons"
    HELPER_TABLE_NAME = "tableFixes"
    HELPER_TABLE_NAME_2 = "tableSkips"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
        self.dedupeTable(self.MOVING_TO_TABLE_NAME)

        for skip_row in self.helper_table_2_rows:
            skip_value = skip_row.get("name_or_tmdb_id").strip()
            self.skip_tokens.add(skip_value.lower())
            self.skip_tokens.add(self.normalizeTitle(skip_value).strip().lower())

        tmdb_fix_ids, tmdb_fix_by_title = set(), {}
        for fix in self.helper_table_rows:
            tmdb_id = fix.get("tmdb_id").strip()
            title_fix = fix.get("title_fix").strip().lower()
            if not tmdb_id or not title_fix:
                continue
            tmdb_id = int(tmdb_id)
            tmdb_fix_ids.add(tmdb_id)
            tmdb_fix_by_title[title_fix] = tmdb_id
            self.tryExceptPass(lambda: tmdb_fix_by_title.__setitem__(self.normalizeTitle(title_fix).strip().lower(), tmdb_id))

        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)
            if row.get("added") or (self.release_date and self.dateToDate(self.release_date) < date.today()):
                continue

            title_raw = (self.english_title or "").strip().lower()
            title_norm = self.normalizeTitle(self.english_title)
            if title_raw in self.skip_tokens or title_norm in self.skip_tokens:
                continue

            if override_tmdb := (tmdb_fix_by_title.get(title_raw) or tmdb_fix_by_title.get(title_norm)):
                if str(override_tmdb).lower() in self.skip_tokens:
                    continue
                self.potential_chosen_id = override_tmdb
                self.non_deduplicated_updates.append({"old_uuid": row.get("id"), "run_id": row.get("run_id"), "english_title": self.english_title, "hebrew_title": self.hebrew_title, "release_date": self.release_date, "tmdb_id": override_tmdb, "imdb_id": None})
                self.processed_ids.add(row.get("id"))
                continue

            # 1) SEARCH TMDB AND COLLECT CANDIDATES
            if self.release_year:
                self.search_plans += [(24, 8, year) for year in (self.release_year, self.release_year - 1, self.release_year + 1)]
            self.search_plans.append((20, None, None))
            for max_total, max_plan, year in self.search_plans:
                if len(self.candidates) >= max_total:
                    continue

                added, page = 0, 1
                while len(self.candidates) < max_total and (max_plan is None or added < max_plan):
                    params = {"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": page}
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
                        if len(self.candidates) == max_total or (max_plan is not None and added == max_plan):
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
            for tmdb_id, movie_details in self.details.items():
                if int(tmdb_id) in tmdb_fix_ids:
                    self.potential_chosen_id = int(tmdb_id)
                    break

            # 4) FALLBACK FIRST/DIRECTOR/RUNTIME RANKING LOGIC
            if self.potential_chosen_id is None:
                first = self.details.get(self.candidates[0])
                if first and (self.normalizeTitle(first.get("title")) == self.normalizeTitle(self.english_title)) and self.release_year and self.tryExceptNone(lambda: int((first.get("release_date") or "")[:4]) == self.release_year):
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

            if not self.potential_chosen_id or str(self.potential_chosen_id).lower() in self.skip_tokens:
                continue

            chosen_details = self.details.get(self.potential_chosen_id) or {}
            chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            self.non_deduplicated_updates.append({"old_uuid": row.get("id"), "run_id": row.get("run_id"), "english_title": self.english_title, "hebrew_title": self.hebrew_title, "release_date": self.release_date, "tmdb_id": self.potential_chosen_id, "imdb_id": chosen_imdb})
            self.processed_ids.add(row.get("id"))

        # 5) DEDUPE BY TMDB ID
        grouped = defaultdict(list)
        for r in self.non_deduplicated_updates:
            if tmdb_id := r.get("tmdb_id"):
                grouped[tmdb_id].append(r)

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
            if not (tmdb_id := row.get("tmdb_id")):
                continue
            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}, timeout=10).json()
            except:
                continue
            if not isinstance(data, dict) or not data.get("id"):
                continue
            external_ids = data.get("external_ids") or {}
            new_row = dict(row)

            new_row["english_title"] = data["title"].strip() if data.get("title") else new_row.get("english_title")
            new_row["imdb_id"] = external_ids.get("imdb_id") or new_row.get("imdb_id")
            new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else new_row.get("poster")
            new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"] if data.get("backdrop_path") else new_row.get("backdrop")
            self.updates.append(new_row)

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
        if self.processed_ids:
            ids = list(self.processed_ids)
            for i in range(0, len(ids), 200):
                chunk = ids[i : i + 200]
                self.supabase.table(self.MAIN_TABLE_NAME).update({"added": True}).in_("id", chunk).execute()
        self.dedupeTable(self.MOVING_TO_TABLE_NAME, ignore_cols={"poster", "backdrop", "release_date", "hebrew_title"}, sort_key=self.comingSoonsFinalDedupeSortKey2)
