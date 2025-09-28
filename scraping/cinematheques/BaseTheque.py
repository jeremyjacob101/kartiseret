from utils.logger import logger

from scraping.utils.InitializeBase import InitializeBase, build_chrome, setUpSupabase, navigate
from scraping.utils.ScrapedFixes import ScrapedFixes
from scraping.utils.SelfFunctions import SelfFunctions
from scraping.utils.FormatAndAppend import AppendToInfo, formatAndUpload


class BaseTheque(SelfFunctions, ScrapedFixes, InitializeBase, AppendToInfo):
    CINEMA_NAME: str
    SCREENING_CITY: str
    URL: str

    def __init__(self, cinema_type, supabase_table_name, id_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = build_chrome()
        self.cinema_type = cinema_type
        self.supabase_table_name = supabase_table_name
        self.id_name = id_name

    def printShowtime(self):
        print(f"{(self.english_title or '')!s:29.29} - {(self.hebrew_title or '')!s:29.29} - {self.CINEMA_NAME!s:12} - {self.release_year!s:4} - {self.original_language!s:10} - {self.screening_city!s:15} - {self.date_of_showing!s:10} - {self.showtime!s:5} - {self.screening_type!s:9} - {self.rating!s:9}".rstrip())

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        had_error = False
        try:
            setUpSupabase(self)  # Sets up supabase client for each cinema
            navigate(self)  # Navigate to website
            self.logic()  # Scraping logic
            formatAndUpload(self)  # Formatting and uploading to supabase
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
