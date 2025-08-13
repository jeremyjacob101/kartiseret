from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from utils.logger import logger
from supabase import create_client

from datetime import datetime
import os, time, pytz, secrets, string


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
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)
        self.sleep = time.sleep
        self.sleep = lambda ms: time.sleep(ms / 1000)

        self.trying_names = []
        self.trying_hrefs = []

        self.items = {"hrefs": [], "titles": [], "runtimes": [], "posters": [], "years": [], "popularity": [], "imdbIDs": [], "dubbedOrNot": []}

    def element(self, path: str):
        if path.startswith(("/", ".//")):
            return self.driver.find_element(By.XPATH, path)
        return self.driver.find_element(By.CSS_SELECTOR, path)

    def elements(self, path: str, contains: str | None = None) -> int:
        if path.startswith(("/", ".//")):
            elements = self.driver.find_elements(By.XPATH, path)
        else:
            elements = self.driver.find_elements(By.CSS_SELECTOR, path)

        if contains is None:
            return len(elements)

        needle = contains.lower()
        count = sum(1 for element in elements if any(needle in (element.get_attribute(attribute) or "").lower() for attribute in ("alt", "class", "id")))
        return count

    def getJlemTimeNow(self):
        return datetime.now(pytz.timezone("Asia/Jerusalem")).isoformat()

    def getRandomHash(self):
        return "".join(secrets.choice(string.digits) for _ in range(20))

    def setUpSupabase(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("Missing  in environment")
        self.supabase = create_client(url, key)

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
