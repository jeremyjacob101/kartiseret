from scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class JAFCtheque(BaseCinema):
    CINEMA_NAME = "Haifa Cinematheque"
    SCREENING_CITY = "Haifa"
    URL = "https://www.jaffacinema.com/"

    def logic(self):
        self.sleep(2)
