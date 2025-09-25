from scraping.cinematheques.BaseTheque import BaseTheque

from datetime import datetime
import re


class JLEMtheque(BaseTheque):
    SOON_CINEMA_NAME = "JLMCT"
    URL = "https://jer-cin.org.il/en/article/4284"

    def logic(self):
        self.sleep(3)

        for _ in range(1, 45):
            self.sleep(1)
            print(self.element("/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[3]/div[3]/a").text.strip())
            today_element = self.element("#calender-filter > p.active")
            today_element.self.element("following-sibling::p").click()

        self.appendToGatheringInfo()
        # self.printCinmathequeShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingSoons").insert(turn_info_into_dictionaries).execute()
