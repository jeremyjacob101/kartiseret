from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict
import requests


class ComingSoonsOmdb(BaseDataflow):
    MAIN_TABLE_NAME = "allSoons"
    MOVING_TO_TABLE_NAME = "finalSoons"
    HELPER_TABLE_NAME = "tableFixes"

    def logic(self):
        for row in self.main_table_rows:
            self.reset_soon_row_state()
            self.load_soon_row(row)

            for fix_row in self.helper_table_rows:
                title_fix = (fix_row.get("title_fix") or "").strip().lower()
                if title_fix == self.english_title.lower():
                    fixed_id = fix_row.get("imdb_id")
                    if fixed_id:
                        self.potential_chosen = fixed_id
                        break

            if self.potential_chosen is None:
                for page in range(1, 5):
                    data = requests.get(f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&s={self.english_title}&type=movie&page={page}").json()
                    if data.get("Response") == "False":
                        break

                    results = data.get("Search", []) or []
                    if page == 1 and results:
                        first = results[0]

                        title_match = first.get("Title", "").strip().lower() == self.english_title.lower()
                        year_match = self.release_year is not None and first.get("Year", "").isdigit() and int(first["Year"]) == self.release_year

                        if title_match and year_match:
                            self.potential_chosen = first.get("imdbID")
                            break
                        self.first_search_result = first.get("imdbID")

                    for movie in results:
                        imdb_id = movie.get("imdbID")
                        if not imdb_id:
                            continue

                        if self.release_year is not None:
                            year_str = movie.get("Year", "")
                            if year_str.isdigit() and abs(int(year_str) - self.release_year) <= 1:
                                self.potential_imdb_ids.append(imdb_id)
                        else:
                            self.potential_imdb_ids.append(imdb_id)

            if self.potential_chosen is None:
                if not self.potential_imdb_ids and self.first_search_result:
                    self.potential_imdb_ids.append(self.first_search_result)
                if not self.potential_imdb_ids:
                    continue

                for imdb_id in self.potential_imdb_ids:
                    try:
                        durl = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&i={imdb_id}"
                        data = requests.get(durl).json()
                        if data.get("Response") == "True":
                            self.details[imdb_id] = data
                    except:
                        continue
                if not self.details:
                    continue

                if self.directed_by:
                    target = self.directed_by.lower()
                    for imdb_id in self.potential_imdb_ids:
                        d = self.details.get(imdb_id)
                        if not d:
                            continue

                        directors = (d.get("Director") or "").lower().split(",")
                        directors = [x.strip() for x in directors if x.strip()]
                        if target in directors:
                            self.potential_chosen = imdb_id
                            break

                if self.potential_chosen is None and self.runtime is not None and self.runtime not in self.fake_runtimes:
                    for imdb_id in self.potential_imdb_ids:
                        d = self.details.get(imdb_id)
                        if not d:
                            continue

                        runtime_field = d.get("Runtime", "N/A")
                        try:
                            candidate_runtime = int(runtime_field.split()[0]) if runtime_field != "N/A" else None
                        except:
                            candidate_runtime = None

                        if candidate_runtime == self.runtime:
                            self.potential_chosen = imdb_id
                            break

                if self.potential_chosen is None:
                    self.potential_chosen = self.potential_imdb_ids[0]

            self.updates.append({"english_title": self.english_title, "hebrew_title": self.hebrew_title, "release_date": self.release_date, "imdb_id": self.potential_chosen})

        grouped = defaultdict(list)
        for row in self.updates:
            grouped[row["imdb_id"]].append(row)

        deduped = []
        for imdb_id, rows in grouped.items():
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

        for row in deduped:
            imdb_id = row.get("imdb_id")
            if not imdb_id:
                continue

            new_row = dict(row)
            tmdb_gave_result = False
            tmdb_data = None
            try:
                tmdb_data = requests.get(
                    f"https://api.themoviedb.org/3/movie/{imdb_id}",
                    params={"api_key": self.TMDB_API_KEY}
                ).json()
            except Exception:
                tmdb_data = None

            if tmdb_data and not tmdb_data.get("success") is False and tmdb_data.get("status_code") not in (34,):
                title = (tmdb_data.get("title") or "").strip()
                poster_path = tmdb_data.get("poster_path")
                if title and poster_path:
                    new_row["english_title"] = title
                    self.english_title = title
                    poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    new_row["poster"] = poster
                    self.poster = poster
                    tmdb_gave_result = True

            if not tmdb_gave_result:
                try:
                    omdb_data = requests.get(
                        f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&i={imdb_id}"
                    ).json()
                except Exception:
                    omdb_data = None

                if omdb_data and omdb_data.get("Response") == "True":
                    new_title = omdb_data.get("Title")
                    new_poster = omdb_data.get("Poster")

                    if new_title and new_title.strip().upper() != "N/A":
                        new_row["english_title"] = new_title.strip()
                        self.english_title = new_title.strip()

                    if new_poster and new_poster.strip().upper() != "N/A":
                        new_row["poster"] = new_poster.strip()
                        self.poster = new_poster.strip()

            self.updates.append(new_row)

        self.upsertUpdates(self.MOVING_TO_TABLE_NAME)
