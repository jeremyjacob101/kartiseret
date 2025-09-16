from scraping.comingsoons.BaseSoon import BaseSoon

from datetime import datetime
import re


class MovieLand(BaseSoon):
    CINEMA_NAME = "MovieLand"
    URL = "https://www.movieland.co.il/soon"

    def logic(self):
        self.sleep(5)
        self.waitAndClick("#sbuzz-confirm", 2)
        self.waitAndClick("#gdpr-module-message > div > div > div.gdpr-content-part.gdpr-accept > a", 2)

        for film_card in range(1, self.lenElements("/html/body/div[1]/div[10]/div[2]/div/div/div") + 1):
            self.trying_hrefs.append(self.element(f"/html/body/div[1]/div[10]/div[2]/div/div/div[{film_card}]/div/div/div/div[1]/a[1]").get_attribute("href"))
        for href in self.trying_hrefs:
            self.driver.get(href)

            

            self.appendToGatheringInfo()
            # self.printComingSoon()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingSoons").insert(turn_info_into_dictionaries).execute()
