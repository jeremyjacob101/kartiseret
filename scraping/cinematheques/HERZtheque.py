from scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HERZtheque(BaseCinema):
    CINEMA_NAME = "Herziliya Cinematheque"
    SCREENING_CITY = "Herziliya"
    URL = "https://hcinema.smarticket.co.il/"

    month_mapping = {"ינואר": "01", "פברואר": "02", "מרץ": "03", "אפריל": "04", "מאי": "05", "יוני": "06", "יולי": "07", "אוגוסט": "08", "ספטמבר": "09", "אוקטובר": "10", "נובמבר": "11", "דצמבר": "12"}

    def logic(self):
        self.sleep(2)

        