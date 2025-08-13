from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from utils.logger import logger
from supabase import create_client

import os, time, pytz, secrets, string
from datetime import datetime

jerusalem_tz = pytz.timezone("Asia/Jerusalem")


class BaseCinema:
    CINEMA_NAME: str
    URL: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self):
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--headless")
        driver_options.add_argument("--disable-gpu")
        driver_options.add_argument("--no-sandbox")
        driver_options.add_argument("--disable-dev-shm-usage")
        driver_options.add_argument("--window-size=1920,1080")
        driver_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=driver_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)
        self.sleep = lambda ms: time.sleep(ms / 1000)

        self.trying_names = []
        self.trying_hrefs = []

        self.showtime_id = None
        self.english_title = None
        self.hebrew_title = None
        self.showtime = None
        self.english_href = None
        self.hebrew_href = None
        self.screening_type = None
        self.audio_language = None
        self.screening_city = None
        self.date_of_showing = None
        self.release_year = None
        self.dubbed_or_not = None
        self.scraped_at = None

        self.gathering_info = {
            "cinema": [],
            "showtime_id": [],
            "english_title": [],
            "hebrew_title": [],
            "showtime": [],
            "english_href": [],
            "hebrew_href": [],
            "screening_type": [],
            "audio_language": [],
            "screening_city": [],
            "date_of_showing": [],
            "release_year": [],
            "dubbed_or_not": [],
            "scraped_at": [],
        }

        self.current_year = datetime.now(jerusalem_tz).year

        self.is_december = datetime.now(jerusalem_tz).month == 12
        self.is_now_december_check = bool

        self.items = {"hrefs": [], "titles": [], "runtimes": [], "posters": [], "years": [], "popularity": [], "imdbIDs": [], "dubbedOrNot": []}

    def element(self, path: str):
        if path.startswith(("/", ".//")):
            return self.driver.find_element(By.XPATH, path)
        return self.driver.find_element(By.CSS_SELECTOR, path)

    def elements(self, path: str, contains: str | None = None) -> int:
        if path.startswith(("/", ".//")):
            elements = self.driver.find_elements(By.XPATH, path)
        else:
            elements = self.driver.find_elements(By.CSS_SELECTOR, path)

        if contains is None:
            return elements

        needle = contains.lower()
        filtered = [element for element in elements if any(needle in (element.get_attribute(attr) or "").lower() for attr in ("alt", "class", "id"))]
        return filtered

    def lenElements(self, path: str, contains: str | None = None) -> int:
        if path.startswith(("/", ".//")):
            elements = self.driver.find_elements(By.XPATH, path)
        else:
            elements = self.driver.find_elements(By.CSS_SELECTOR, path)

        if contains is None:
            return len(elements)

        needle = contains.lower()
        count = sum(1 for element in elements if any(needle in (element.get_attribute(attribute) or "").lower() for attribute in ("alt", "class", "id")))
        return count

    def getJlemTimeNow(self):
        return datetime.now(pytz.timezone("Asia/Jerusalem")).isoformat()

    def switchSupabaseCreatedAtToJlem(self):
        return

    def getRandomHash(self):
        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))

    def setUpSupabase(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("Missing  in environment")
        self.supabase = create_client(url, key)

    def appendToGatheringInfo(self):
        self.gathering_info["cinema"].append(self.CINEMA_NAME)
        self.gathering_info["showtime_id"].append(self.showtime_id)
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["showtime"].append(self.showtime)
        self.gathering_info["english_href"].append(self.english_href)
        self.gathering_info["hebrew_href"].append(self.hebrew_href)
        self.gathering_info["screening_type"].append(self.screening_type)
        self.gathering_info["audio_language"].append(self.audio_language)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["date_of_showing"].append(self.date_of_showing)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["dubbed_or_not"].append(self.dubbed_or_not)
        self.gathering_info["scraped_at"].append(self.scraped_at)

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        try:
            self.setUpSupabase()  # Sets up supabase client for each cinema
            self.navigate()  # Navigate to website
            self.logic()  # Scraping logic
        except Exception:
            logger.error(
                "\n\n\n\t\t-------- ERROR --------\n\n\n[%s] unhandled error at url=%s\n\n\n\t\t-------- ERROR --------\n\n\n",
                getattr(self, "CINEMA_NAME", "?"),
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
            )

        self.driver.quit()
