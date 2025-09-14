from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import logger
from supabase import create_client

import os, time, pytz, secrets, string
from datetime import datetime

jerusalem_tz = pytz.timezone("Asia/Jerusalem")


class BaseSoon:
    SOON_CINEMA_NAME: str
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
        self.sleep = lambda s=None: time.sleep(999999999 if s is None else s)

        self.current_year = str(datetime.now(jerusalem_tz).year)
        self.current_month = str(datetime.now(jerusalem_tz).month)

        self.trying_names = []
        self.trying_hebrew_names = []
        self.trying_hrefs = []
        self.original_languages = []
        self.ratings = []
        self.release_years = []
        self.directed_bys = []
        self.runtimes = []
        self.release_dates = []

        self.coming_soon_id = None
        self.english_title = None
        self.hebrew_title = None
        self.original_language = None
        self.release_year = None
        self.scraped_at = None
        self.rating = None
        self.directed_by = None
        self.runtime = None
        self.release_date = None
        self.helper_id = None
        self.helper_type = None

        self.gathering_info = {
            "cinema": [],
            "coming_soon_id": [],
            "english_title": [],
            "hebrew_title": [],
            "original_language": [],
            "release_year": [],
            "scraped_at": [],
            "rating": [],
            "directed_by": [],
            "runtime": [],
            "release_date": [],
            "helper_id": [],
            "helper_type": [],
        }

    def element(self, path: str):
        return self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

    def elements(self, path: str, contains: str | None = None) -> int:
        elements = self.driver.find_elements(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

        if contains is None:
            return elements

        needle = contains.lower()
        filtered = [element for element in elements if any(needle in (element.get_attribute(attr) or "").lower() for attr in ("alt", "class", "id"))]
        return filtered

    def lenElements(self, path: str, contains: str | None = None) -> int:
        elements = self.driver.find_elements(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

        if contains is None:
            return len(elements)

        needle = contains.lower()
        count = sum(1 for element in elements if any(needle in (element.get_attribute(attribute) or "").lower() for attribute in ("alt", "class", "id")))
        return count

    def click(self, path: str, sleepafter: float = 0.0):
        self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path).click()
        self.sleep(sleepafter)

    def jsClick(self, path: str, sleepafter: float = 0.15):
        self.driver.execute_script("arguments[0].click();", self.element(path))
        self.sleep(sleepafter)

    def jsRemove(self, path: str, sleepafter: float = 0.5):
        self.driver.execute_script("document.querySelector(arguments[0]).remove();", path)
        self.sleep(sleepafter)

    def waitAndClick(self, path: str, sleepafter: float = 0.5):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path))).click()
        self.sleep(sleepafter)

    def zoomOut(self, percentage: int, sleepafter: float = 0.2):
        self.driver.execute_script(f"document.body.style.zoom='{percentage}%'")
        self.sleep(sleepafter)

    def getJlemTimeNow(self):
        return datetime.now(pytz.timezone("Asia/Jerusalem")).isoformat()

    def getRandomHash(self):
        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))

    def setUpSupabase(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase = create_client(url, key)

    def appendToGatheringInfo(self):
        self.fixLanguage()
        self.fixRating()

        self.gathering_info["cinema"].append(self.SOON_CINEMA_NAME)
        self.gathering_info["coming_soon_id"].append(str(self.getRandomHash()))
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["original_language"].append(self.original_language)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["release_date"].append(self.release_date)
        self.gathering_info["helper_id"].append(self.helper_id)
        self.gathering_info["helper_type"].append(self.helper_type)

    def fixLanguage(self):
        replace = {
            "EN": "English",
            "FR": "French",
            "HE": "Hebrew",
            "HEB": "Hebrew",
            "CZ": "Czech",
            "KO": "Korean",
            "GER": "German",
            "JAP": "Japanese",
            "DAN": "Danish",
            "אנגלית": "English",
            "עברית": "Hebrew",
            "דנית": "Danish",
            "צרפתית": "French",
            "גרמנית": "German",
            "הינדי": "Hindi",
            "יעודכן בקרוב": None,
        }
        self.original_language = replace.get(self.original_language, self.original_language)

    def fixRating(self):
        replace = {
            "No limit": "All",
            "מותר לכל": "All",
            "הותר לכל": "All",
            "מותר לכל הגילאים": "All",
            "הגבלת גיל: הותר לכל הגילאים": "All",
            "Allowed for all ages": "All",
            "הותר מגיל 18": "18+",
            "הגבלת גיל: הותר מגיל 16 בהצגת תעודה מזהה": "16+",
            "הותר מגיל 16": "16+",
            "הגבלת גיל: הותר מגיל 14": "14+",
            "הותר מגיל 14": "14+",
            "הגבלת גיל: הותר מגיל 12": "12+",
            "הותר מגיל 12": "12+",
            "הותר מגיל 9": "9+",
            "עד גיל 8 בליווי מבוגר": "9+",
            "Other": None,
            "אחר": None,
            "יעודכן בקרוב": None,
            "הגבלת גיל: טרם נקבע": None,
            "טרם נקבע": None,
            "": None,
        }
        self.rating = replace.get(self.rating, self.rating)

    def printComingSoon(self):
        print(f"{(self.english_title or '')!s:29.29} - {(self.hebrew_title or '')!s:29.29} - {self.SOON_CINEMA_NAME!s:12} - {self.release_date!s:4}")

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        had_error = False
        try:
            self.setUpSupabase()  # Sets up supabase client for each cinema
            self.navigate()  # Navigate to website
            self.logic()  # Scraping logic
        except Exception:
            logger.error(
                "\n\n\n\t\t-------- ERROR --------\n\n\n[%s] unhandled error at url=%s\n\n\n\t\t-------- ERROR --------\n\n\n",
                getattr(self, "SOON_CINEMA_NAME", "?"),
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
            )

            try:
                from utils.logger import dump_artifacts  # local import to avoid changing module imports

                png, html = dump_artifacts(getattr(self, "driver", None), prefix=getattr(self, "SOON_CINEMA_NAME", self.__class__.__name__))
                print(f"[{getattr(self, 'SOON_CINEMA_NAME', self.__class__.__name__)}] Saved artifacts:\n" f"  screenshot: {png}\n" f"  html:       {html}")
            except Exception as capture_err:
                print(f"[{getattr(self, 'SOON_CINEMA_NAME', self.__class__.__name__)}] Failed to dump artifacts: {capture_err}")
            raise

        self.driver.quit()
