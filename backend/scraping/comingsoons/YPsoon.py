from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class YPsoon(BaseCinema):
    CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    month_mapping = {"January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06", "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"}

    def logic(self):
        self.sleep(10)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        for film_card in range(1, self.lenElements("/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div") + 1):
            self.english_hrefs.append(self.element(f"/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a").get_attribute("href"))
        for href in self.english_hrefs:
            self.driver.get(href)
            self.sleep(0.1)

            self.english_title = self.element("/html/body/div[5]/section[1]/div/div[2]/div[1]/div/ul/li/h1").text.strip()
            self.hebrew_title = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[1]/dd").text.strip()

            release_year = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text.strip()
            self.release_year = self.ifElseNone(re.search(r"\b\d{4}\b", release_year), int(re.search(r"\b\d{4}\b", release_year).group(0)))

            directed_by = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[4]/dd").text.strip())
            self.directed_by = self.ifElseNone(directed_by, directed_by)

            original_language = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[6]/dd").text.strip())
            if "HEB" in original_language or original_language == "":
                original_language = "HEB"
            self.original_language = original_language

            rating = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[7]/dd").text.strip()
            self.rating = self.ifElseNone(rating, str(rating))

            runtime = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[2]/p").text.strip()
            self.runtime = self.ifElseNone(runtime and (m := re.search(r"\d+", runtime)), int(m.group()))

            release_date = str(self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[1]/p").text.strip())
            d, m, y = release_date.split()
            release_date = f"{d}/{self.month_mapping[m]}/{y}"
            self.release_date = datetime.strptime(release_date, "%d/%m/%Y").date().isoformat()

            self.helper_id = href
            self.helper_type = "href"

            self.appendToGatheringInfo()
