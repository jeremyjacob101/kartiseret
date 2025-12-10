from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    MOVING_TO_TABLE_NAME = "testingFinalSoons2"
    HELPER_TABLE_NAME = "testingIMDbFixes"

    def logic(self):
        stats = {
            "imdb_fix": 0,
            "title_year": 0,
            "director": 0,
            "runtime": 0,
            "fallback_first": 0,
        }
        index_stats = {i: 0 for i in range(1, 16)}

        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            print("--------------------------------------------------")
            print(f"PROCESSING: {self.english_title} ({self.release_year})")

            candidates = []
            details = {}

            # --------------------------------------------------
            # 1) SEARCH TMDB AND COLLECT FIRST ~15 RESULTS
            # --------------------------------------------------
            page = 1
            while len(candidates) < 15:
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

                    if len(candidates) >= 15:
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
                        stats["imdb_fix"] += 1
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
                        stats["title_year"] += 1

                # director match
                if self.potential_chosen is None and self.directed_by:
                    target = self.directed_by.lower()
                    for tmdb_id, d in details.items():
                        crew = d.get("credits", {}).get("crew", [])
                        directors = [c["name"].lower() for c in crew if c.get("job") == "Director" and c.get("name")]
                        if target in directors:
                            self.potential_chosen = tmdb_id
                            print(f"DIRECTOR MATCH ({self.directed_by}) → TMDB {tmdb_id}")
                            stats["director"] += 1
                            break

                # runtime match
                if self.potential_chosen is None and self.runtime and self.runtime not in self.fake_runtimes:
                    for tmdb_id, d in details.items():
                        if d.get("runtime") == self.runtime:
                            self.potential_chosen = tmdb_id
                            print(f"RUNTIME MATCH ({self.runtime}) → TMDB {tmdb_id}")
                            stats["runtime"] += 1
                            break

                # last resort
                if self.potential_chosen is None:
                    self.potential_chosen = candidates[0]
                    print(f"FALLBACK FIRST RESULT → TMDB {self.potential_chosen}")
                    stats["fallback_first"] += 1

            chosen_imdb = None
            if self.potential_chosen:
                chosen_details = details.get(self.potential_chosen) or {}
                chosen_imdb = (chosen_details.get("external_ids", {}) or {}).get("imdb_id")

            print(f"CHOSEN → {self.english_title} | TMDB {self.potential_chosen} | IMDb {chosen_imdb}")
            if self.potential_chosen in candidates:
                idx = candidates.index(self.potential_chosen) + 1  # 1-based
                index_stats[idx] += 1
                print(f"USED ORIGINAL RESULT INDEX: {idx}")
            else:
                print("WARNING: CHOSEN TMDB ID NOT IN ORIGINAL CANDIDATES")

            self.updates.append(
                {
                    "english_title": self.english_title,
                    "hebrew_title": self.hebrew_title,
                    "release_date": self.release_date,
                    "tmdb_id": self.potential_chosen,
                    "imdb_id": chosen_imdb,
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
        enrich_stats = {
            "title_hit": 0,
            "title_poster_hit": 0,
        }

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

            has_title = False
            has_poster = False

            if data.get("title"):
                new_row["english_title"] = data["title"].strip()
                has_title = True
            if data.get("poster_path"):
                new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"]
                has_poster = True
            if data.get("backdrop_path"):
                new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"]
                has_poster = True

            if has_title:
                enrich_stats["title_hit"] += 1
            if has_title and has_poster:
                enrich_stats["title_poster_hit"] += 1

            enriched.append(new_row)

        self.updates = enriched
        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)

        print("==================================================")
        print("TMDB MATCHING SUMMARY")
        print("--------------------------------------------------")
        print(f"IMDb fix matches        : {stats['imdb_fix']}")
        print(f"Title + year matches    : {stats['title_year']}")
        print(f"Director matches        : {stats['director']}")
        print(f"Runtime matches         : {stats['runtime']}")
        print(f"Fallback to first result: {stats['fallback_first']}")
        print("==================================================")

        print("--------------------------------------------------")
        print("TMDB ENRICHMENT SUMMARY")
        print(f"Title hits           : {enrich_stats['title_hit']}")
        print(f"Title + poster hits  : {enrich_stats['title_poster_hit']}")
        print("--------------------------------------------------")

        print("==================================================")
        print("TMDB ORIGINAL INDEX USED TIMES")
        print("--------------------------------------------------")

        for i in range(1, 16):
            print(f"{i:2d}. : {index_stats[i]}")

        print("==================================================")
