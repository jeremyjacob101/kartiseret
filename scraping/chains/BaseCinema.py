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
        return self.driver.find_element(By.XPATH, xpath)

    def elementsXPATH(self, xpath: str):
        return len(self.driver.find_elements(By.XPATH, xpath))

    def elementCSS(self, css: str):
        return self.driver.find_element(By.CSS_SELECTOR, css)

    def elementsCSS(self, css: str):
        return len(self.driver.find_elements(By.CSS_SELECTOR, css))

    def navigate(self):
        self.driver.get(self.URL)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def scrape(self):
        self.navigate()
        self.logic(self.items)
