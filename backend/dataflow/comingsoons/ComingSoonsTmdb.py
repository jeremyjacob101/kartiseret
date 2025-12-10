from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    MOVING_TO_TABLE_NAME = "testingFinalSoons2"
    HELPER_TABLE_NAME = "testingIMDbFixes"

    def logic(self):
        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            print("--------------------------------------------------")
            print(f"PROCESSING: {self.english_title} ({self.release_year})")

            candidates = []
            details = {}

            # --------------------------------------------------
            # 1) SEARCH TMDB AND COLLECT FIRST ~30 RESULTS
            # --------------------------------------------------
            page = 1
            while len(candidates) < 30:
                print(f"TMDB SEARCH | page={page}")

                params = {
                    "api_key": self.TMDB_API_KEY,
                    "query": self.english_title,
                    "page": page,
                }

                try:
                    r = requests.get(
                        "https://api.themoviedb.org/3/search/movie",
                        params=params,
                        timeout=10,
                    ).json()
                except Exception as e:
                    print("SEARCH ERROR:", e)
                    break

                results = r.get("results") or []
                if not results:
                    break

                for m in results:
                    tmdb_id = m.get("id")
                    if tmdb_id:
                        candidates.append(tmdb_id)
                        print(f"  candidate → TMDB {tmdb_id}")

                    if len(candidates) >= 30:
                        break

                page += 1

            if not candidates:
                print("NO SEARCH RESULTS – SKIPPING")
                continue

            # --------------------------------------------------
            # 2) FETCH FULL DETAILS (external_ids + credits)
            # --------------------------------------------------
            for tmdb_id in candidates:
                try:
                    print(f"FETCH DETAILS | TMDB {tmdb_id}")
                    m = requests.get(
                        f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                        params={
                            "api_key": self.TMDB_API_KEY,
                            "append_to_response": "external_ids,credits",
                        },
                        timeout=10,
                    ).json()

                    if m.get("id"):
                        details[tmdb_id] = m
                except Exception as e:
                    print("DETAIL ERROR:", e)

            if not details:
                print("NO DETAILS FETCHED – SKIPPING")
                continue

            # --------------------------------------------------
            # 3) IMDb FIX TABLE HARD MATCH
            # --------------------------------------------------
            for tmdb_id, d in details.items():
                imdb_id = d.get("external_ids", {}).get("imdb_id")
                if not imdb_id:
                    continue

                for fix in self.helper_table_rows:
                    if fix.get("imdb_id") == imdb_id:
                        self.potential_chosen = tmdb_id
                        print(f"IMDB FIX MATCH | IMDb {imdb_id} → TMDB {tmdb_id}")
                        break

                if self.potential_chosen:
                    break

            # --------------------------------------------------
            # 4) FALLBACK RANKING LOGIC
            # --------------------------------------------------
            if self.potential_chosen is None:
                print("NO IMDb FIX MATCH – APPLYING HEURISTICS")

                # exact title + year bias on first result
                first_id = candidates[0]
                first = details.get(first_id)

                if first:
                    title_match = self.normalizeTitle(first.get("title") or "").strip().lower() == str(self.english_title).strip().lower()

                    year_match = False
                    if self.release_year and first.get("release_date"):
                        try:
                            year_match = int(first["release_date"][:4]) == self.release_year
                        except:
                            pass

                    if title_match and year_match:
                        self.potential_chosen = first_id
                        print(f"TITLE+YEAR MATCH → TMDB {first_id}")

                # director match
                if self.potential_chosen is None and self.directed_by:
                    target = self.directed_by.lower()
                    for tmdb_id, d in details.items():
                        crew = d.get("credits", {}).get("crew", [])
                        directors = [c["name"].lower() for c in crew if c.get("job") == "Director" and c.get("name")]
                        if target in directors:
                            self.potential_chosen = tmdb_id
                            print(f"DIRECTOR MATCH ({self.directed_by}) → TMDB {tmdb_id}")
                            break

                # runtime match
                if self.potential_chosen is None and self.runtime and self.runtime not in self.fake_runtimes:
                    for tmdb_id, d in details.items():
                        if d.get("runtime") == self.runtime:
                            self.potential_chosen = tmdb_id
                            print(f"RUNTIME MATCH ({self.runtime}) → TMDB {tmdb_id}")
                            break

                # last resort
                if self.potential_chosen is None:
                    self.potential_chosen = candidates[0]
                    print(f"FALLBACK FIRST RESULT → TMDB {self.potential_chosen}")

            print(f"CHOSEN → {self.english_title} | TMDB {self.potential_chosen}")

            self.updates.append(
                {
                    "english_title": self.english_title,
                    "hebrew_title": self.hebrew_title,
                    "release_date": self.release_date,
                    "tmdb_id": self.potential_chosen,
                }
            )

        # --------------------------------------------------
        # 5) DEDUPE BY TMDB ID
        # --------------------------------------------------
        grouped = defaultdict(list)
        for row in self.updates:
            grouped[row["tmdb_id"]].append(row)

        deduped = []
        for tmdb_id, rows in grouped.items():
            rows_sorted = sorted(rows, key=self.comingSoonsFinalDedupeSortKey)
            best = rows_sorted[0]

            if (best.get("hebrew_title") or "").strip() in ("", "null"):
                for r in rows_sorted:
                    ht = (r.get("hebrew_title") or "").strip()
                    if ht not in ("", "null"):
                        best["hebrew_title"] = ht
                        break

            deduped.append(best)

        self.updates = deduped
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)

        # --------------------------------------------------
        # 6) ENRICH TITLE + POSTER
        # --------------------------------------------------
        enriched = []
        for row in deduped:
            tmdb_id = row.get("tmdb_id")
            if not tmdb_id:
                continue

            try:
                data = requests.get(
                    f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                    params={"api_key": self.TMDB_API_KEY},
                    timeout=10,
                ).json()
            except Exception as e:
                print("ENRICH ERROR:", e)
                continue

            new_row = dict(row)

            if data.get("title"):
                new_row["english_title"] = data["title"].strip()

            if data.get("poster_path"):
                new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"]

            enriched.append(new_row)

        self.updates = enriched
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
