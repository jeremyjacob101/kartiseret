from scraping.cinematheques.BaseTheque import BaseTheque

from datetime import datetime
import re


class JLEMtheque(BaseTheque):
    SOON_CINEMA_NAME = "JLMCT"
    URL = "https://jer-cin.org.il/en/article/4284"

    def logic(self):
        self.sleep(3)

        for _ in range(1,45):
            today_element = self.element("#calender-filter > p.active")
            
            today_element.self.element("following-sibling::p").click()

        self.appendToGatheringInfo()
        # self.printCinmathequeShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingSoons").insert(turn_info_into_dictionaries).execute()
