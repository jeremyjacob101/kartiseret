from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import logger
from supabase import create_client

import os, pytz, secrets, string
from datetime import datetime

from scraping.utils.InitializeBase import InitializeBase, build_chrome
from scraping.utils.ScrapedFixes import ScrapedFixes
from scraping.utils.SelfFunctions import SelfFunctions


class BaseSoon(SelfFunctions, ScrapedFixes, InitializeBase):
    CINEMA_NAME: str
    URL: str

    def __init__(self, cinema_type, supabase_table_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = build_chrome()
        self.cinema_type = cinema_type
        self.supabase_table_name = supabase_table_name

    def setUpSupabase(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase = create_client(url, key)

    def printComingSoon(self):
        print(f"{(self.english_title or '')!s:29.29} - {(self.hebrew_title or '')!s:29.29} - {self.CINEMA_NAME!s:12} - {self.release_date!s:4}")

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
        self.gathering_info["release_date"].append(self.release_date)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["helper_id"].append(self.helper_id)
        self.gathering_info["helper_type"].append(self.helper_type)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["cinema"].append(self.CINEMA_NAME)
        self.gathering_info[f"{self.cinema_type}"].append(str(self.getRandomHash()))

    def formatAndUpload(self):
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

        return self.supabase.table(self.supabase_table_name).insert(rows).execute()

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
