from scraping.BaseCinema import BaseCinema

from datetime import datetime

from selenium.webdriver.common.by import By


class SSCtheque(BaseCinema):
    CINEMA_NAME = "Sam Spiegel Cinema"
    SCREENING_CITY = "Jerusalem"
    URL = "https://jer-cin.org.il/en/article/4284"

    def logic(self):
        self.sleep(3)
