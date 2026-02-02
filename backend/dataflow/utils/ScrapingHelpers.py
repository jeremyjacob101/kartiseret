from selenium.webdriver.common.by import By
import time


class ScrapingHelpers:
    def element(self, path: str):
        try:
            return self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)
        except Exception:
            time.sleep(0.25)
            return self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)
