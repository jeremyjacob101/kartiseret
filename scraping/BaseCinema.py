from utils.logger import logger, dump_artifacts, artifactPrinting

from scraping.utils.InitializeBase import InitializeBase, build_chrome, setUpSupabase, navigate
from scraping.utils.FormatAndAppend import AppendToInfo, formatAndUpload
from scraping.utils.sScrapedFixes import ScrapedFixes
from scraping.utils.sSelfFunctions import SelfFunctions


class BaseCinema(SelfFunctions, ScrapedFixes, InitializeBase, AppendToInfo):
    CINEMA_NAME: str
    SCREENING_CITY: str
    URL: str
    HEADLESS: bool = True

    def __init__(self, cinema_type, supabase_table_name, id_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = build_chrome(self.HEADLESS)
        self.cinema_type = cinema_type
        self.supabase_table_name = supabase_table_name
        self.id_name = id_name

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        try:
            setUpSupabase(self)  # Sets up supabase client for each cinema
            navigate(self)  # Navigate to website
            self.logic()  # Scraping logic
            formatAndUpload(self)  # Formatting and uploading to supabase
        except Exception:
            artifactPrinting(self)
            raise

        self.driver.quit()
