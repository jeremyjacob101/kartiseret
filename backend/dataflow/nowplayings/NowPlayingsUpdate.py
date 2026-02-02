from backend.dataflow.BaseDataflow import BaseDataflow
import requests


class NowPlayingsUpdate(BaseDataflow):
    MAIN_TABLE_NAME = "finalMovies"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)

        for row in self.main_table_rows:
            self.reset_np_main_row_state()
            self.load_update_final_movies_main_row(row)

            # TMDb
            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{self.tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}, timeout=10).json()
            except:
                continue

            new_row = dict(row)
            new_row["english_title"] = data["title"].strip() if data.get("title") else self.english_title
            new_row["runtime"] = data["runtime"] if data.get("runtime") is not None else self.runtime
            new_row["popularity"] = data["popularity"] if data.get("popularity") is not None else self.popularity
            new_row["imdb_id"] = data.get("external_ids", {}).get("imdb_id") or self.imdb_id
            new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else self.poster
            new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"] if data.get("backdrop_path") else self.backdrop
            new_row["release_year"] = data["release_date"][:4] if data.get("release_date") else self.release_year
            new_row["tmdbRating"] = int(round(data["vote_average"] * 10)) if data.get("vote_average") is not None else self.tmdbRating
            new_row["tmdbVotes"] = data["vote_count"] if data.get("vote_count") is not None else self.tmdbVotes

            self.updates.append(new_row)
            self.upsertUpdates(self.MAIN_TABLE_NAME)
            self.dedupeTable(self.MAIN_TABLE_NAME, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)

            # Letterboxd

            # IMDb

            # Rotten Tomatoes
