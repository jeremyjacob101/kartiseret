from selenium import webdriver
from datetime import datetime
import time, pytz, os
from supabase import create_client


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


def navigate(self):
    self.driver.get(self.URL)


def build_chrome(headless: bool = True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size=1920,1080")
    options.add_argument(f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.0 Safari/537.36")
    return webdriver.Chrome(options=options)


class InitializeBase:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep = lambda s=None: time.sleep(999999999 if s is None else s)

        self.current_year = str(datetime.now(pytz.timezone("Asia/Jerusalem")).year)
        self.current_month = str(datetime.now(pytz.timezone("Asia/Jerusalem")).month)

        self.showtimes = []
        self.english_titles = []
        self.hebrew_titles = []
        self.english_hrefs = []
        self.hebrew_hrefs = []
        self.screening_types = []
        self.original_languages = []
        self.dub_languages = []
        self.date_of_showings = []
        self.release_years = []
        self.release_dates = []
        self.directed_bys = []
        self.runtimes = []
        self.ratings = []
        self.screening_citys = []
        self.helper_ids = []
        self.helper_types = []

        self.showtime = None
        self.english_title = None
        self.hebrew_title = None
        self.english_href = None
        self.hebrew_href = None
        self.screening_type = None
        self.original_language = None
        self.dub_language = None
        self.date_of_showing = None
        self.release_year = None
        self.release_date = None
        self.directed_by = None
        self.runtime = None
        self.rating = None
        self.screening_city = None
        self.helper_id = None
        self.helper_type = None

        self.gathering_info = {
            "showtime": [],
            "english_title": [],
            "hebrew_title": [],
            "english_href": [],
            "hebrew_href": [],
            "screening_type": [],
            "original_language": [],
            "dub_language": [],
            "date_of_showing": [],
            "release_year": [],
            "release_date": [],
            "directed_by": [],
            "runtime": [],
            "rating": [],
            "screening_city": [],
            "helper_id": [],
            "helper_type": [],
            "theque_showtime_id": [],
            "coming_soon_id": [],
            "showtime_id": [],
            "scraped_at": [],
            "cinema": [],
        }
