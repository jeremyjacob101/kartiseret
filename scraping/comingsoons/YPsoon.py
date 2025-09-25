from scraping.comingsoons.BaseSoon import BaseSoon

from datetime import datetime
import re


class YPsoon(BaseSoon):
    SOON_CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    def logic(self):
        self.sleep(10)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        for film_card in range(1, self.lenElements("/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div") + 1):
            self.trying_hrefs.append(self.element(f"/html/body/div[6]/section/div[4]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a").get_attribute("href"))
        for href in self.trying_hrefs:
            self.driver.get(href)
            self.sleep(0.1)

            self.english_title = self.element("/html/body/div[5]/section[1]/div/div[2]/div[1]/div/ul/li/h1").text.strip()
            self.hebrew_title = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/dl/div[1]/dd").text.strip()

            trying_year = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text
            if re.search(r"\b\d{4}\b", trying_year):
                self.release_year = int(re.search(r"\b\d{4}\b", trying_year).group(0))
            else:
                self.release_years = None

            self.directed_by = str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(4) > dd").text.strip())

            original_language = str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(6) > dd").text)
            if "HEB" in original_language or original_language == "":
                original_language = "HEB"
            self.original_languages = original_language

            rating = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(7) > dd").text
            if rating:
                self.ratings = str(rating)

            runtime = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[2]/p").text.strip()
            if runtime and (m := re.search(r"\d+", runtime)):
                self.runtime = int(m.group())

            self.appendToGatheringInfo()
            # self.printComingSoon()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingSoons").insert(turn_info_into_dictionaries).execute()
