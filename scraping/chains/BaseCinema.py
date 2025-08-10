from settings import (
    webdriver,
    headless_options,
    By,
    WebDriverWait,
    ActionChains,
    EC,
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    current_year,
    current_date,
    name_present_day,
    new_formatted_date,
    threading,
    time,
    csv,
    requests,
    pd,
    re,
    datetime,
    timedelta,
)

from utils.logger import logger


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

        self.items = {
            "hrefs": [],
            "titles": [],
            "runtimes": [],
            "posters": [],
            "years": [],
            "popularity": [],
            "imdbIDs": [],
            "imdbScores": [],
            "imdbVotes": [],
            "rtScores": [],
        }

    def elementXPATH(self, xpath: str):
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except Exception:
            logger.debug(
                "elementXPATH failed xpath=%r url=%s",
                xpath,
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
                stacklevel=2,
            )
        raise

    def elementsXPATH(self, xpath: str):
        try:
            els = self.driver.find_elements(By.XPATH, xpath)
            logger.debug(
                "elementsXPATH xpath=%r -> %d url=%s",
                xpath,
                len(els),
                getattr(self.driver, "current_url", "?"),
                stacklevel=2,
            )
            return len(els)
        except Exception:
            logger.debug(
                "elementsXPATH crashed xpath=%r url=%s",
                xpath,
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
                stacklevel=2,
            )
            return 0

    def elementCSS(self, css: str):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, css)
        except Exception:
            logger.debug(
                "elementCSS failed css=%r url=%s",
                css,
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
                stacklevel=2,
            )
            raise

    def elementsCSS(self, css: str):
        try:
            els = self.driver.find_elements(By.CSS_SELECTOR, css)
            logger.debug(
                "elementsCSS css=%r -> %d url=%s",
                css,
                len(els),
                getattr(self.driver, "current_url", "?"),
                stacklevel=2,
            )
            return len(els)
        except Exception:
            logger.debug(
                "elementsCSS crashed css=%r url=%s",
                css,
                getattr(self.driver, "current_url", "?"),
                exc_info=True,
                stacklevel=2,
            )
            return 0

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        self.navigate()
        self.logic(self.items)
