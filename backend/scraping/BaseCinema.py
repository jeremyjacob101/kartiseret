from backend.scraping.utils.InitializeBaseCinema import InitializeBaseCinema, build_chrome, setUpSupabase, navigate, logSuccessfulRun
from backend.scraping.utils.FormatAndAppend import AppendToInfo, formatAndUpload, formatAndWriteCsv
from backend.scraping.utils.ScrapedFixes import ScrapedFixes
from backend.scraping.utils.ScrapingHelpers import ScrapingHelpers


class BaseCinema(ScrapingHelpers, ScrapedFixes, InitializeBaseCinema, AppendToInfo):
    CINEMA_NAME: str
    SCREENING_CITY: str
    URL: str
    HEADLESS: bool = True

    def __init__(self, cinema_type, supabase_table_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = build_chrome(self.HEADLESS)
        self.cinema_type = cinema_type
        self.supabase_table_name = supabase_table_name

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        try:
            setUpSupabase(self)
            navigate(self)
            self.logic()
            # formatAndUpload(self)
            logSuccessfulRun(self)
        except Exception:
            formatAndWriteCsv(self)
            raise
