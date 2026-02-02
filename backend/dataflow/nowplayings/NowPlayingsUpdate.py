from backend.dataflow.BaseDataflow import BaseDataflow
import requests, re


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
            new_row["lb_id"] = f"tmdb/{new_row['imdb_id']}" if new_row.get("imdb_id") else self.lb_id

            self.updates.append(new_row)
            self.upsertUpdates(self.MAIN_TABLE_NAME)
            self.dedupeTable(self.MAIN_TABLE_NAME, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)

            # Letterboxd
            self.driver.get(f"https://www.letterboxd.com/{self.lb_id}")

            new_row = dict(row)
            try:
                new_row["lbRating"] = self.element("/html/body/div[2]/div/div[2]/div[2]/aside/section[2]/span/a").text.strip
            except:
                new_row["lbRating"] = self.lbRating

            try:
                new_row["lbVotes"] = re.search(r"based on\s+([\d,]+)\s+ratings", self.element("/html/body/div[2]/div/div[2]/div[2]/aside/section[2]/span/a").get_attribute("data-original-title") or "").group(1).replace(",", "")
            except:
                new_row["lbVotes"] = self.lbVotes

            # IMDb
            self.driver.get(f"https://www.imdb.com/title/{self.imdb_id}")

            new_row = dict(row)
            try:
                new_row["imdbRating"] = self.element("/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]").text.strip()
            except:
                new_row["imdbRating"] = self.imdbRating

            try:
                t = (self.element("/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[3]").text or "").strip().upper().replace(",", "")
                new_row["imdbRating"] = int(float(t[:-1]) * (1000 if t.endswith("K") else 1000000 if t.endswith("M") else 1)) if t else self.imdbRating
            except:
                new_row["imdbRating"] = self.imdbRating

            # Rotten Tomatoes
