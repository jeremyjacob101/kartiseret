from backend.dataflow.BaseDataflow import BaseDataflow
import requests


class ComingSoonsOmdb(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"

    def logic(self):
        for row in self.main_table_rows:
            english_title = str(row["english_title"]) if row.get("english_title") not in (None, "", "null") else ""
            release_year = int(row["release_year"]) if row.get("release_year") not in (None, "", "null") else None
            row_director = str(row["directed_by"]) if row.get("directed_by") not in (None, "", "null") else ""
            row_runtime = int(row["runtime"]) if row.get("runtime") not in (None, "", "null") else None

            print(f"\n=== {english_title} ===")

            potential_imdb_ids: list[str] = []
            first_search_imdb_id: str | None = None

            # ---------- 1) collect potential_imdb_ids from search ----------
            for page in range(1, 5):
                try:
                    omdb_url = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&s={english_title}&type=movie&page={page}"
                    data = requests.get(omdb_url).json()
                except Exception as e:
                    print(f"OMDb search error for {english_title!r} page {page}: {e}")
                    continue

                if data.get("Response") == "False":
                    if page == 1:
                        print(f"\n\n\n\nOMDb Error - NO RESULTS\n\n\n\n")
                    print(f"OMDb no response for {english_title!r} page {page}")
                    break

                results = data.get("Search", []) or []

                # EARLY MATCH SHORTCUT — if first search result is an exact match (title + year)
                if page == 1 and results:
                    first = results[0]
                    title_match = first.get("Title", "").lower().strip() == english_title.lower().strip()
                    year_match = release_year is not None and first.get("Year", "").isdigit() and abs(int(first["Year"]) - release_year) <= 0
                    if title_match and year_match:
                        CHOSEN_IMDB_ID = first.get("imdbID")
                        print(f"Exact match shortcut: {english_title} ({release_year}) -> {CHOSEN_IMDB_ID}")
                        # skip entire rest of the logic for this movie
                        break

                for movie in results:
                    imdb_id = str(movie.get("imdbID"))
                    if not imdb_id:
                        continue

                    # keep track of the very first search result for hard fallback
                    if first_search_imdb_id is None:
                        first_search_imdb_id = imdb_id

                    # filter by release_year if we have one
                    if release_year is not None:
                        candidate_year = int(movie.get("Year"))
                        if candidate_year is not None and abs(candidate_year - release_year) <= 1:
                            potential_imdb_ids.append(imdb_id)
                    else:
                        # no release_year on the row => append all results
                        potential_imdb_ids.append(imdb_id)

            # If we filtered by year and got nothing, fall back to "first ever" result
            if not potential_imdb_ids and first_search_imdb_id:
                potential_imdb_ids.append(first_search_imdb_id)

            if not potential_imdb_ids:
                print(f"No OMDb candidates found for {english_title!r}")
                continue  # or handle however you want

            # ---------- 2) fetch full details for each candidate ----------
            details_by_id: dict[str, dict] = {}
            for imdb_id in potential_imdb_ids:
                if imdb_id in details_by_id:
                    continue
                try:
                    omdb_url = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&i={imdb_id}"
                    data = requests.get(omdb_url).json()
                except Exception as e:
                    print(f"OMDb detail error for {imdb_id}: {e}")
                    continue

                if data.get("Response") == "True":
                    details_by_id[imdb_id] = data

            if not details_by_id:
                print(f"No valid detail responses for {english_title!r}")
                continue

            # ---------- 3) director-based pick ----------
            chosen_imdb_id: str | None = None

            if row_director:
                target_director_lower = row_director.lower()
                for imdb_id in potential_imdb_ids:
                    data = details_by_id.get(imdb_id)
                    if not data:
                        continue

                    director_field = (data.get("Director") or "").lower()
                    if not director_field:
                        continue

                    # OMDb "Director" can contain multiple names separated by commas
                    directors = [d.strip() for d in director_field.split(",") if d.strip()]
                    if target_director_lower in directors:
                        chosen_imdb_id = imdb_id
                        print(f"Matched by director: {row_director} -> {imdb_id}")
                        break

            # ---------- 4) runtime-based pick ----------
            if chosen_imdb_id is None and row_runtime is not None:
                # normalize fake runtimes to minutes
                if row_runtime not in self.fake_runtimes:
                    for imdb_id in potential_imdb_ids:
                        data = details_by_id.get(imdb_id)
                        if not data:
                            continue
                        candidate_runtime = int(data.get("Runtime").split()[0]) if data.get("Runtime") != "N/A" else None
                        if candidate_runtime is not None and candidate_runtime == row_runtime:
                            chosen_imdb_id = imdb_id
                            print(f"Matched by runtime: {row_runtime} min -> {imdb_id}")
                            break

            # ---------- 5) final fallback: first in potential_imdb_ids ----------
            if chosen_imdb_id is None:
                chosen_imdb_id = potential_imdb_ids[0]
                print(f"No director/runtime hit; falling back to {chosen_imdb_id}")
            if CHOSEN_IMDB_ID is None:
                CHOSEN_IMDB_ID = chosen_imdb_id
            print(f"FINAL CHOSEN_IMDB_ID for {english_title!r}: {CHOSEN_IMDB_ID}")
