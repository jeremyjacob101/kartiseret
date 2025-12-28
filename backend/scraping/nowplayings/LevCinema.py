from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class LevCinema(BaseCinema):
    CINEMA_NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        for tab_view in (1, 2):
            stale_hrefs = self.elements(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li", "featureItem")

            for href in [self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li[{i}]/div/a[1]").get_attribute("href") for i in range(1, len(stale_hrefs) + 1)]:
                raise
                hebrew_title_href = re.sub(r"(/)en(/)", r"\1", href)
                self.driver.get(hebrew_title_href)
                self.hebrew_title = str(self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text)

                self.driver.get(href)

                self.english_title = str(self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text)
                if "dubbed" in self.english_title.lower():
                    self.english_title = re.sub(r"\b[dD]ubbed\b", "", self.english_title).strip()
                    self.hebrew_title = self.hebrew_title.replace("מדובב", "").strip()
                    self.dub_language = "Hebrew"
                if "dubbded" in self.english_title.lower():
                    self.english_title = re.sub(r"\b[dD]ubbded\b", "", self.english_title).strip()
                    self.hebrew_title = self.hebrew_title.replace("מדובב", "").strip()
                    self.dub_language = "Hebrew"
                if isinstance(self.hebrew_title, str) and self.hebrew_title.endswith(" אנגלית"):
                    self.hebrew_title = self.hebrew_title[: -len(" אנגלית")].strip()

                self.release_year = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]").text
                self.release_year = int(m.group(0)) if (m := re.search(r"\b(19|20)\d{2}\b", self.release_year)) else None

                self.original_language = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]").text
                self.original_language = str(m.group(1)) if (m := re.search(r"^\s*([A-Za-z]+)", self.original_language)) else "Hebrew"

                self.rating = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[3]").text
                self.rating = str(self.rating.split(":", 1)[1].strip()) if self.rating else "All"

                runtime = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[3]").text
                if runtime and runtime.isdigit():
                    self.runtime = runtime

                for city in range(1, self.lenElements("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div") + 1):
                    self.screening_city = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/h3").text)

                    crossed_year = False
                    trying_year = self.current_year
                    for day in range(1, self.lenElements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div") + 1):
                        self.date_of_showing = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/span").text
                        self.date_of_showing = re.search(r"\d{1,2}/\d{1,2}", self.date_of_showing).group(0)
                        dd, mm = re.search(r"(\d{1,2})/(\d{1,2})", self.date_of_showing).groups()
                        if self.current_month == "12" and not crossed_year and (str(mm) == "1" or str(mm) == "01" or str(mm) == "2" or str(mm) == "02" or str(mm) == "3" or str(mm) == "03" or str(mm) == "4" or str(mm) == "04"):
                            crossed_year = True
                            trying_year = str(int(trying_year) + 1)
                        yyyy = str(trying_year)
                        self.date_of_showing = datetime.strptime(f"{yyyy}/{dd}/{mm}", "%Y/%d/%m").date().isoformat()

                        for time in range(1, self.lenElements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div") + 1):
                            self.showtime = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").text)
                            self.english_href = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").get_attribute("href") + "?lang=en")
                            self.hebrew_href = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").get_attribute("href") + "?lang=he")
                            self.screening_type = "Regular"
                            self.screening_tech = "2D"

                            self.appendToGatheringInfo()

            self.driver.get(self.URL)
