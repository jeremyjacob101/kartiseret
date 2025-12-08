from backend.dataflow.BaseDataflow import BaseDataflow
import requests


class ComingSoonsOmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    HELPER_TABLE_NAME = "testingIMDbFixes"

    def logic(self):
        for row in self.main_table_rows:
            self.load_row(row)
            print(f"\n{self.english_title}")

            for fix_row in self.helper_table_rows:
                title_fix = (fix_row.get("title_fix") or "").strip().lower()
                if title_fix == self.english_title.lower():
                    fixed_id = fix_row.get("imdbID")
                    if fixed_id:
                        self.potential_chosen = fixed_id
                        break

            if self.potential_chosen is None:
                for page in range(1, 5):
                    url = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&s={self.english_title}&type=movie&page={page}"
                    data = requests.get(url).json()

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

            self.CHOSEN_IMDB_ID = self.potential_chosen
            print(self.CHOSEN_IMDB_ID)
