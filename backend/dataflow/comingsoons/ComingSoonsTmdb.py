from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests


class ComingSoonsTmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    MOVING_TO_TABLE_NAME = "testingFinalSoons"
    HELPER_TABLE_NAME = "testingIMDbFixes"

    TMDB_BASE = "https://api.themoviedb.org/3"

    def logic(self):
        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            # 1. helper table override (imdb -> tmdb mapping assumed)
            for fix_row in self.helper_table_rows:
                title_fix = (fix_row.get("title_fix") or "").strip().lower()
                if title_fix == self.english_title.lower():
                    fixed_id = fix_row.get("tmdb_id")
                    if fixed_id:
                        self.potential_chosen = fixed_id
                        print(f"{self.english_title:30} | {self.potential_chosen}")
                        break

            # 2. search TMDb
            if self.potential_chosen is None:
                for page in range(1, 5):
                    params = {"api_key": self.TMDB_API_KEY, "query": self.english_title, "page": page}

                    r = requests.get(f"{self.TMDB_BASE}/search/movie", params=params).json()
                    results = r.get("results", []) or []

                    if not results:
                        break

                    if page == 1:
                        first = results[0]
                        title_match = (first.get("title") or "").strip().lower() == self.english_title.lower()

                        year_match = False
                        if self.release_year and first.get("release_date"):
                            try:
                                year_match = int(first["release_date"][:4]) == self.release_year
                            except:
                                year_match = False

                        if title_match and year_match:
                            self.potential_chosen = first.get("id")
                            print(f"{self.english_title:30} | {self.potential_chosen}")
                            break

                        self.first_search_result = first.get("id")

                    for movie in results:
                        tmdb_id = movie.get("id")
                        if not tmdb_id:
                            continue

                        if self.release_year and movie.get("release_date"):
                            try:
                                y = int(movie["release_date"][:4])
                                if abs(y - self.release_year) <= 1:
                                    self.potential_imdb_ids.append(tmdb_id)
                                    print(f"{self.english_title:30} | {tmdb_id}")
                            except:
                                pass
                        else:
                            self.potential_imdb_ids.append(tmdb_id)
                            print(f"{self.english_title:30} | {tmdb_id}")

            # 3. deep inspection
            if self.potential_chosen is None:
                if not self.potential_imdb_ids and self.first_search_result:
                    self.potential_imdb_ids.append(self.first_search_result)

                if not self.potential_imdb_ids:
                    continue

                for tmdb_id in self.potential_imdb_ids:
                    try:
                        m = requests.get(f"{self.TMDB_BASE}/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY}).json()

                        c = requests.get(f"{self.TMDB_BASE}/movie/{tmdb_id}/credits", params={"api_key": self.TMDB_API_KEY}).json()

                        if m.get("id"):
                            m["_credits"] = c
                            self.details[tmdb_id] = m
                    except:
                        continue

                if not self.details:
                    continue

                # director match
                if self.directed_by:
                    target = self.directed_by.lower()
                    for tmdb_id in self.potential_imdb_ids:
                        d = self.details.get(tmdb_id)
                        if not d:
                            continue

                        crew = d.get("_credits", {}).get("crew", [])
                        directors = [x["name"].lower() for x in crew if x.get("job") == "Director" and x.get("name")]

                        if target in directors:
                            self.potential_chosen = tmdb_id
                            print(f"{self.english_title:30} | {self.potential_chosen}")
                            break

                # runtime match
                if self.potential_chosen is None and self.runtime and self.runtime not in self.fake_runtimes:
                    for tmdb_id in self.potential_imdb_ids:
                        d = self.details.get(tmdb_id)
                        if not d:
                            continue

                        if d.get("runtime") == self.runtime:
                            self.potential_chosen = tmdb_id
                            print(f"{self.english_title:30} | {self.potential_chosen}")
                            break

                if self.potential_chosen is None:
                    self.potential_chosen = self.potential_imdb_ids[0]
                    print(f"{self.english_title:30} | {self.potential_chosen}")

            self.updates.append({"english_title": self.english_title, "hebrew_title": self.hebrew_title, "release_date": self.release_date, "tmdb_id": self.potential_chosen})

        # dedupe identical TMDb IDs
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

        # enrich title + poster
        for row in deduped:
            tmdb_id = row.get("tmdb_id")
            if not tmdb_id:
                continue

            new_row = dict(row)

            data = requests.get(f"{self.TMDB_BASE}/movie/{tmdb_id}", params={"api_key": self.TMDB_API_KEY}).json()

            if data.get("title"):
                new_row["english_title"] = data["title"].strip()
                self.english_title = data["title"].strip()

            if data.get("poster_path"):
                poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
                new_row["poster"] = poster
                self.poster = poster

            self.updates.append(new_row)

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
