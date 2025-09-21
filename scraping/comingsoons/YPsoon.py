from scraping.comingsoons.BaseSoon import BaseSoon

from datetime import datetime
import re


class YPsoon(BaseSoon):
    SOON_CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    def logic(self):
        self.sleep(10)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        self.appendToGatheringInfo()
        # self.printComingSoon()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
