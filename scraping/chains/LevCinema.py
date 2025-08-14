from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class LevCinema(BaseCinema):
    CINEMA_NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        for tab_view in (1, 2):
            stale_hrefs = self.elements(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li", "featureItem")

            for href in [self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li[{i}]/div/a[1]").get_attribute("href") for i in range(1, len(stale_hrefs) + 1)]:
                hebrew_title_href = re.sub(r"(/)en(/)", r"\1", href)
                self.driver.get(hebrew_title_href)
                self.hebrew_title = str(self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text)

                self.driver.get(href)

                self.english_title = str(self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text)
                self.dubbed_or_not = "dubbed" in self.english_title.lower()
                if self.dubbed_or_not:
                    self.english_title = re.sub(r"\b[dD]ubbed\b", "", self.english_title).strip()
                    self.hebrew_title = self.hebrew_title.replace("מדובב", "").strip()

                self.release_year = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]").text
                self.release_year = int(m.group(0)) if (m := re.search(r"\b(19|20)\d{2}\b", self.release_year)) else None

                self.original_language = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]").text
                self.original_language = str(m.group(1)) if (m := re.search(r"^\s*([A-Za-z]+)", self.original_language)) else ""

                self.rating = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[3]").text
                self.rating = str(self.rating.split(":", 1)[1].strip()) if self.rating else "All"
                if self.rating == "Allowed for all ages":
                    self.rating = "All"

                for city in range(1, self.lenElements("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div") + 1):
                    self.screening_city = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/h3").text)

                    crossed_year = False
                    for day in range(1, self.lenElements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div") + 1):
                        self.date_of_showing = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/span").text
                        self.date_of_showing = re.search(r"\d{1,2}/\d{1,2}", self.date_of_showing).group(0)

                        dd, mm = re.search(r"(\d{1,2})/(\d{1,2})", self.date_of_showing).groups()
                        yyyy = str(self.current_year)
                        if self.current_month == "12" and not crossed_year and str(mm) == "1":
                            crossed_year = True
                            yyyy = str(int(yyyy) + 1)

                        self.date_of_showing = datetime.strptime(f"{yyyy}/{dd}/{mm}", "%Y/%d/%m").date().isoformat()

                        for time in range(1, self.lenElements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div") + 1):
                            self.showtime = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").text)
                            self.english_href = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").get_attribute("href") + "?lang=en")
                            self.hebrew_href = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").get_attribute("href") + "?lang=he")
                            self.screening_type = "Regular"

                            self.appendToGatheringInfo()
                            self.printShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
