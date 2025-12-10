from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class YPsoon(BaseCinema):
    CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    month_mapping = {"January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06", "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"}
    first_click = False

    def logic(self):
        self.sleep(10)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        for film_card in range(1, self.lenElements("/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div") + 1):
            self.english_hrefs.append(self.element(f"/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a").get_attribute("href"))
        for href in self.english_hrefs:

            if href.endswith("s2r2") or href.endswith("s2r2/"):
                continue

            self.driver.get(href)
            self.sleep(0.1)

            if not self.first_click:
                self.tryExceptPass(lambda: self.element("/html/body/div[15]/div/div/div/div[2]/div[3]/div[1]/div/h2/small").click())
                self.first_click = True

            self.english_title = self.element("/html/body/div[5]/section[1]/div/div[2]/div[1]/div/ul/li/h1").get_attribute("textContent").strip()
            self.hebrew_title = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[1]/dd").get_attribute("textContent").strip()
            if "gaming live" in self.hebrew_title.lower():
                continue

            release_year = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").get_attribute("textContent").strip()
            self.release_year = int(m.group(0)) if (m := re.search(r"\b\d{4}\b", release_year)) else None

            directed_by = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[4]/dd").get_attribute("textContent").strip())
            self.directed_by = self.ifElseNone(directed_by, directed_by)

            original_language = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[6]/dd").get_attribute("textContent").strip())
            if "HEB" in original_language or original_language == "":
                original_language = "HEB"
            self.original_language = original_language

            rating = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[7]/dd").get_attribute("textContent").strip()
            self.rating = self.ifElseNone(rating, str(rating))

            runtime = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[2]/p").get_attribute("textContent").strip()
            self.runtime = int(m.group()) if (runtime and (m := re.search(r"\d+", runtime))) else None

            release_date = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[1]/p").get_attribute("textContent").strip())
            d, m, y = release_date.split()
            release_date = f"{d}/{self.month_mapping[m]}/{y}"
            self.release_date = datetime.strptime(release_date, "%d/%m/%Y").date().isoformat()

            self.helper_id = href

            self.appendToGatheringInfo()
