from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
        self.directed_by = None
        self.runtime = None
        self.rating = None
        self.screening_city = None

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
            "directed_by": [],
            "runtime": [],
            "rating": [],
            "scraped_at": [],
            "showtime_id": [],
            "cinema": [],
            "screening_city": [],
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
        self.fixScreeningType()
        self.fixCinemaName()
        self.fixLanguage()
        self.fixRating()

        self.gathering_info["showtime"].append(self.showtime)
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["english_href"].append(self.english_href)
        self.gathering_info["hebrew_href"].append(self.hebrew_href)
        self.gathering_info["screening_type"].append(self.screening_type)
        self.gathering_info["original_language"].append(self.original_language)
        self.gathering_info["dub_language"].append(self.dub_language)
        self.gathering_info["date_of_showing"].append(self.date_of_showing)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["showtime_id"].append(str(self.getRandomHash()))
        self.gathering_info["cinema"].append(self.CINEMA_NAME)
        self.gathering_info["screening_city"].append(self.screening_city)

    def fixCinemaName(self):
        replace = {
            "Lev Smadar": "Jerusalem",
            "Lev Omer": "Omer",
            "Even Yehuda": "Even Yehuda",
            "Ramat Hasharon": "Ramat Hasharon",
            "Lev Raanana": "Raanana",
            "Lev Shoham": "Shoham",
            "Lev Daniel": "Herziliya",
            "לוח הקרנות ב רב חן גבעתיים": "Givatayim",
            "לוח הקרנות ב רב חן דיזינגוף": "Tel Aviv",
            "לוח הקרנות ב רב חן קרית אונו": "Kiryat Ono",
            "SCREENINGS FOR PLANET BEER SHEVA": "Beer Sheva",
            "SCREENINGS FOR PLANET AYALON": "Ayalon",
            "SCREENINGS FOR PLANET RISHON LETZIYON": "Rishon Letzion",
            "SCREENINGS FOR PLANET ZICHRON YAAKOV": "Zichron Yaakov",
            "SCREENINGS FOR PLANET JERUSALEM": "Jerusalem",
            "SCREENINGS FOR PLANET HAIFA": "Haifa",
            "כרמיאל": "Carmiel",
            "חיפה": "Haifa",
            "נתניה": "Netanya",
            'הצוק ת"א': "Glilot",
            "עפולה": "Afula",
            'עזריאלי ת"א Summer Sky': "Azrieli Rooftop",
            "HOT CINEMA כרמיאל": "Carmiel",
            "HOT CINEMA נהריה": "Nahariya",
            "HOT CINEMA קריון": "Kiryat Bialik",
            "HOT CINEMA חיפה": "Haifa",
            "HOT CINEMA כפר סבא": "Kfar Saba",
            "HOT CINEMA פתח תקווה": "Petach Tikvah",
            "HOT CINEMA מודיעין": "Modiin",
            "HOT CINEMA רחובות": "Rehovot",
            "HOT CINEMA אשדוד": "Ashdod",
            "HOT CINEMA אשקלון": "Ashkelon",
            "סינמה סיטי גלילות": "Glilot",
            "סינמה סיטי גלילות": "Glilot",
            "סינמה סיטי גלילות (ONYX)": "Glilot",
            "סינמה סיטי גלילות (VIP)": "Glilot",
            "סינמה סיטי גלילות (Lounge)": "Glilot",
            'סינמה סיטי ראשל"צ': "Rishon Letzion",
            'סינמה סיטי ראשל"צ (VIP)': "Rishon Letzion",
            'סינמה סיטי ראשל"צ (VIP לייט)': "Rishon Letzion",
            "סינמה סיטי ירושלים": "Jerusalem",
            "סינמה סיטי ירושלים (VIP)": "Jerusalem",
            "סינמה סיטי כפר-סבא": "Kfar Saba",
            "סינמה סיטי כפר סבא (Prime)": "Kfar Saba",
            "סינמה סיטי נתניה": "Netanya",
            "סינמה סיטי נתניה (Prime)": "Netanya",
            "סינמה סיטי באר שבע": "Beer Sheva",
            "סינמה סיטי באר שבע (VIP)": "Beer Sheva",
            "סינמה סיטי אשדוד": "Ashdod",
            "סינמה סיטי חדרה": "Chadera",
            "סינמה סיטי חדרה (Prime)": "Chadera",
        }
        self.screening_city = replace.get(self.screening_city, self.screening_city)

    def fixScreeningType(self):
        replace = {
            "VIP LIGHT": "VIP Light",
            "סינמה סיטי גלילות": "Regular",
            "סינמה סיטי גלילות (Lounge)": "Lounge",
            "סינמה סיטי גלילות (ONYX)": "4DX",
            "סינמה סיטי גלילות (VIP)": "VIP",
            'סינמה סיטי ראשל"צ': "Regular",
            'סינמה סיטי ראשל"צ (VIP)': "VIP",
            'סינמה סיטי ראשל"צ (VIP לייט)': "VIP Light",
            "סינמה סיטי ירושלים": "Regular",
            "סינמה סיטי ירושלים (VIP)": "VIP",
            "סינמה סיטי כפר-סבא": "Regular",
            "סינמה סיטי כפר סבא (Prime)": "Prime",
            "סינמה סיטי נתניה": "Regular",
            "סינמה סיטי נתניה (Prime)": "Prime",
            "סינמה סיטי באר שבע": "Regular",
            "סינמה סיטי באר שבע (VIP)": "VIP",
            "סינמה סיטי אשדוד": "Regular",
            "סינמה סיטי חדרה": "Regular",
            "סינמה סיטי חדרה (Prime)": "Prime",
        }
        self.screening_type = replace.get(self.screening_type, self.screening_type)

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

    def printShowtime(self):
        print(f"{(self.english_title or '')!s:29.29} - {(self.hebrew_title or '')!s:29.29} - {self.CINEMA_NAME!s:12} - {self.release_year!s:4} - {self.original_language!s:10} - {self.screening_city!s:15} - {self.date_of_showing!s:10} - {self.showtime!s:5} - {self.screening_type!s:9} - {self.rating!s:9}".rstrip())

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
                getattr(self, "CINEMA_NAME", "?"),
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
            )

            try:
                from utils.logger import dump_artifacts  # local import to avoid changing module imports

                png, html = dump_artifacts(getattr(self, "driver", None), prefix=getattr(self, "CINEMA_NAME", self.__class__.__name__))
                print(f"[{getattr(self, 'CINEMA_NAME', self.__class__.__name__)}] Saved artifacts:\n" f"  screenshot: {png}\n" f"  html:       {html}")
            except Exception as capture_err:
                print(f"[{getattr(self, 'CINEMA_NAME', self.__class__.__name__)}] Failed to dump artifacts: {capture_err}")
            raise

        self.driver.quit()
