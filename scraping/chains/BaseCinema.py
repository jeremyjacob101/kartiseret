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
        # driver_options.add_argument("--headless")
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
        self.dub_languages = []
        self.ratings = []
        self.release_years = []
        self.directed_bys = []

        self.showtime_id = None
        self.english_title = None
        self.hebrew_title = None
        self.showtime = None
        self.english_href = None
        self.hebrew_href = None
        self.screening_type = None
        self.original_language = None
        self.screening_city = None
        self.date_of_showing = None
        self.release_year = None
        self.dub_language = None
        self.scraped_at = None
        self.rating = None
        self.directed_by = None

        self.gathering_info = {
            "cinema": [],
            "showtime_id": [],
            "english_title": [],
            "hebrew_title": [],
            "showtime": [],
            "english_href": [],
            "hebrew_href": [],
            "screening_type": [],
            "original_language": [],
            "screening_city": [],
            "date_of_showing": [],
            "release_year": [],
            "dub_language": [],
            "scraped_at": [],
            "rating": [],
            "directed_by": [],
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

    def click(self, path: str):
        self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path).click()

    def jsClick(self, path: str):
        self.driver.execute_script("arguments[0].click();", self.element(path))
        self.sleep(0.1)

    def waitAndClick(self, path: str):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path))).click()
        self.sleep(1)

    def zoomOut(self, percentage: int):
        self.driver.execute_script(f"document.body.style.zoom='{percentage}%'")
        self.sleep(1)

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
        self.fixCinemaNames()

        self.gathering_info["cinema"].append(self.CINEMA_NAME)
        self.gathering_info["showtime_id"].append(str(self.getRandomHash()))
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["showtime"].append(self.showtime)
        self.gathering_info["english_href"].append(self.english_href)
        self.gathering_info["hebrew_href"].append(self.hebrew_href)
        self.gathering_info["screening_type"].append(self.screening_type)
        self.gathering_info["original_language"].append(self.original_language)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["date_of_showing"].append(self.date_of_showing)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["dub_language"].append(self.dub_language)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["directed_by"].append(self.directed_by)

    def fixCinemaNames(self):
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

    def printShowtime(self):
        print(f"{self.english_title!s:29} - {self.hebrew_title!s:29} - {self.CINEMA_NAME!s:12} - {self.release_year!s:4} - {self.original_language!s:10} - {self.screening_city!s:15} - {self.date_of_showing!s:10} - {self.showtime!s:5} - {self.screening_type!s:9} - {self.rating!s:9}")

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
