from backend.dataflow.BaseDataflow import BaseDataflow
import requests, re


class NowPlayingsUpdate(BaseDataflow):
    MAIN_TABLE_NAME = "finalMovies"
    HEADLESS = False

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)

        for row in self.main_table_rows:
            self.reset_np_main_row_state()
            self.load_update_final_movies_main_row(row)
            new_row = dict(row)

            # TMDb
            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{self.tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}, timeout=10).json()
            except:
                continue

            new_row["english_title"] = data["title"].strip() if data.get("title") else self.english_title
            new_row["runtime"] = data["runtime"] if data.get("runtime") is not None else self.runtime
            new_row["popularity"] = data["popularity"] if data.get("popularity") is not None else self.popularity
            new_row["imdb_id"] = data.get("external_ids", {}).get("imdb_id") or self.imdb_id
            new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else self.poster
            new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"] if data.get("backdrop_path") else self.backdrop
            new_row["release_year"] = data["release_date"][:4] if data.get("release_date") else self.release_year
            new_row["tmdbRating"] = int(round(data["vote_average"] * 10)) if data.get("vote_average") is not None else self.tmdbRating
            new_row["tmdbVotes"] = data["vote_count"] if data.get("vote_count") is not None else self.tmdbVotes
            new_row["lb_id"] = f"tmdb/{self.tmdb_id}"

            # # Letterboxd
            # self.driver.get(f"https://www.letterboxd.com/{new_row['lb_id']}")

            # try:
            #     new_row["lbRating"] = self.element("/html/body/div[2]/div/div[2]/div[2]/aside/section[2]/span/a").text.strip()
            # except:
            #     new_row["lbRating"] = self.lbRating

            # try:
            #     new_row["lbVotes"] = int(re.search(r"based on\s+([\d,]+)\s+ratings", self.element("/html/body/div[2]/div/div[2]/div[2]/aside/section[2]/span/a").get_attribute("data-original-title") or "").group(1).replace(",", ""))
            # except:
            #     new_row["lbVotes"] = self.lbVotes

            # IMDb
            if new_row.get("imdb_id") is not None and new_row.get("imdb_id") != "":
                self.driver.get(f"https://www.imdb.com/title/{new_row['imdb_id']}")

                try:
                    new_row["imdbRating"] = self.element("/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]").text.strip()
                except:
                    new_row["imdbRating"] = self.imdbRating

                try:
                    t = (self.element("/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[3]").text or "").strip().upper().replace(",", "")
                    new_row["imdbVotes"] = int(float(t[:-1]) * (1000 if t.endswith("K") else 1000000 if t.endswith("M") else 1)) if t else self.imdbVotes
                except:
                    new_row["imdbVotes"] = self.imdbVotes

            # Rotten Tomatoes
            self.driver.get(f"https://www.rottentomatoes.com/search?search={new_row['english_title']} {new_row['release_year']}")
            try:
                self.driver.get(self.element("/html/body/div[3]/main/div/div/section[1]/div/search-page-result[1]/ul/search-page-media-row[1]/a[1]").get_attribute("href"))
            except:
                pass

            try:
                new_row["rtAudienceRating"] = int(re.sub(r"[^\d]", "", (self.element("/html/body/div[3]/main/div/div[1]/div[2]/div[1]/div[1]/media-scorecard/rt-text[3]").get_attribute("innerHTML") or "").strip()))
            except:
                new_row["rtAudienceRating"] = self.rtAudienceRating

            try:
                new_row["rtCriticRating"] = int(re.sub(r"[^\d]", "", (self.element("/html/body/div[3]/main/div/div[1]/div[2]/div[1]/div[1]/media-scorecard/rt-text[1]").get_attribute("innerHTML") or "").strip()))
            except:
                new_row["rtCriticRating"] = self.rtCriticRating

            try:
                new_row["rtAudienceVotes"] = int((re.search(r"([\d,]+)\s*\+?", (self.element("/html/body/div[3]/main/div/div[1]/div[2]/div[1]/div[1]/media-scorecard/rt-link[2]").text or "")).group(1)).replace(",", ""))
            except:
                new_row["rtAudienceVotes"] = self.rtAudienceVotes

            try:
                new_row["rtCriticVotes"] = int((re.search(r"([\d,]+)", (self.element("/html/body/div[3]/main/div/div[1]/div[2]/div[1]/div[1]/media-scorecard/rt-link[1]").text or "")).group(1)).replace(",", ""))
            except:
                new_row["rtCriticVotes"] = self.rtCriticVotes

            print(new_row)
            self.updates.append(new_row)

        if self.updates:
            self.upsertUpdates(self.MAIN_TABLE_NAME)
            self.dedupeTable(self.MAIN_TABLE_NAME, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)
