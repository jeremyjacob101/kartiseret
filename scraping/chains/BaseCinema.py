from settings import headless_options, webdriver, By, WebDriverWait, ActionChains, time

from utils.logger import logger
import os
from supabase import create_client
from imdbInfo import getImdbInfo


class BaseCinema:
    URL: str
    NAME: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self):
        self.driver = webdriver.Chrome(options=headless_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)
        self.sleep = time.sleep
        self.sleep = lambda ms: time.sleep(ms / 1000)

        self.trying_names = []
        self.trying_hrefs = []

        self.items = {"hrefs": [], "titles": [], "runtimes": [], "posters": [], "years": [], "popularity": [], "imdbIDs": [], "imdbScores": [], "imdbVotes": [], "rtScores": [], "dubbedOrNot": []}

        self.supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

    def element(self, path: str):
        if path.startswith(("/", ".//")):
            return self.driver.find_element(By.XPATH, path)
        return self.driver.find_element(By.CSS_SELECTOR, path)

    def elements(self, path: str, contains: str | None = None) -> int:
        if path.startswith(("/", ".//")):
            elems = self.driver.find_elements(By.XPATH, path)
        else:
            elems = self.driver.find_elements(By.CSS_SELECTOR, path)

        if contains is None:
            return len(elems)

        needle = contains.lower()
        return sum(1 for el in elems if any(needle in (el.get_attribute(attr) or "").lower() for attr in ("alt", "class", "id")))

    # def setup_supabase(self):
    #     url = os.environ.get("SUPABASE_URL")
    #     key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    #     if not url or not key:
    #         raise RuntimeError(f"Missing env vars: SUPABASE_URL={url!r}, SUPABASE_SERVICE_ROLE_KEY={key!r}")
    #     return create_client(url, key)

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def imdbInfo(self):
        getImdbInfo(self.items)

    def scrape(self):
        try:
            # self.setup_supabase()
            self.navigate()  # Navigate to website
            self.logic()  # Scraping logic
            self.imdbInfo()  # Get imdbInfo
        except Exception:
            logger.error(
                "\n\n\n\t\t-------- ERROR --------\n\n\n[%s] unhandled error at url=%s\n\n\n\t\t-------- ERROR --------\n\n\n",
                getattr(self, "NAME", "?"),
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
            )

        self.driver.quit()
