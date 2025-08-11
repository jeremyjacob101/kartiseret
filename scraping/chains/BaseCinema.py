from settings import headless_options, webdriver, By, WebDriverWait, ActionChains, time

from utils.logger import logger
import os
from supabase import create_client
from dotenv import load_dotenv
from imdbInfo import getImdbInfo

def get_env(name: str) -> str:
    # Load .env locally, has no effect in Actions if already set
    load_dotenv()
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val

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

    def setup_supabase(self):
        url = get_env("SUPABASE_URL")
        key = get_env("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase = create_client(url, key)

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def imdbInfo(self):
        getImdbInfo(self.items)

    def scrape(self):
        try:
            self.setup_supabase()
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
