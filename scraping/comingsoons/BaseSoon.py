from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import logger
from supabase import create_client

import os, pytz, secrets, string
from datetime import datetime

from scraping.utils.scrapedFixes import fixLanguage, fixRating, fixCinemaName, fixScreeningType
from scraping.utils.initializeBases import build_chrome, initialize_fields


class BaseSoon:
    CINEMA_NAME: str
    URL: str
    SUPABASE_TABLE_NAME = "testingSoons"
    CINEMA_TYPE = "comingSoon"

    fixLanguage = fixLanguage
    fixRating = fixRating
    fixCinemaName = fixCinemaName
    fixScreeningType = fixScreeningType

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self):
        self.driver = build_chrome()
        initialize_fields(self)

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

    def printComingSoon(self):
        print(f"{(self.english_title or '')!s:29.29} - {(self.hebrew_title or '')!s:29.29} - {self.CINEMA_NAME!s:12} - {self.release_date!s:4}")

    def appendToGatheringInfo(self, cinema_type=CINEMA_TYPE):
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
        self.gathering_info["release_date"].append(self.release_date)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["helper_id"].append(self.helper_id)
        self.gathering_info["helper_type"].append(self.helper_type)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["cinema"].append(self.CINEMA_NAME)

        if cinema_type == "cinematheque":
            self.gathering_info["theque_showtime_id"].append(str(self.getRandomHash()))
        if cinema_type == "comingSoon":
            self.gathering_info["coming_soon_id"].append(str(self.getRandomHash()))
        if cinema_type == "nowPlaying":
            self.gathering_info["showtime_id"].append(str(self.getRandomHash()))

    def formatAndUpload(self, table_name=SUPABASE_TABLE_NAME):
        info = getattr(self, "gathering_info", {})
        if not isinstance(info, dict):
            return None

        active_columns = [name for name, values in info.items() if isinstance(values, list) and len(values) > 0]
        max_rows = max((len(info[name]) for name in active_columns), default=0)

        rows = []
        for row_index in range(max_rows):
            row_data = {}
            for column_name in active_columns:
                column_values = info[column_name]
                value = column_values[row_index] if row_index < len(column_values) else None
                if (isinstance(value, str) and (value := value.strip())) or (value is not None and (not hasattr(value, "__len__") or len(value) > 0)):
                    row_data[column_name] = value
            rows.append(row_data)

        return self.supabase.table(table_name).insert(rows).execute()

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
            self.formatAndUpload()  # Formatting and uploading to supabase
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
