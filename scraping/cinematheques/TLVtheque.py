from scraping.BaseCinema import BaseCinema

from selenium.webdriver.common.by import By
from datetime import datetime, timedelta


class TLVtheque(BaseCinema):
    CINEMA_NAME = "Jerusalem Cinematheque"
    SCREENING_CITY = "Jerusalem"
    URL = "https://www.cinema.co.il/en/shown/"

    def logic(self):
        self.sleep(3)

        current_date = self.today_date
        end_date = current_date + timedelta(days=60)
        while current_date <= end_date:
            date_string = current_date.strftime("%Y-%m-%d")
            self.driver.get(f"https://www.cinema.co.il/en/shown/?date={date_string}")
