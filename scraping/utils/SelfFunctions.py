from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime
import pytz, secrets, string


class SelfFunctions:
    def element(self, path: str):
        return self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

    def elements(self, path: str, contains: str | None = None) -> int:
        elements = self.driver.find_elements(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

        if contains is None:
            return elements

        needle = contains.lower()
        filtered = [element for element in elements if any(needle in (element.get_attribute(attr) or "").lower() for attr in ("alt", "class", "id"))]
        return filtered

    def lenElements(self, path: str, contains: str | None = None) -> int:
        elements = self.driver.find_elements(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path)

        if contains is None:
            return len(elements)

        needle = contains.lower()
        count = sum(1 for element in elements if any(needle in (element.get_attribute(attribute) or "").lower() for attribute in ("alt", "class", "id")))
        return count

    def click(self, path: str, sleepafter: float = 0.0):
        self.driver.find_element(By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path).click()
        self.sleep(sleepafter)

    def jsClick(self, path: str, sleepafter: float = 0.15):
        self.driver.execute_script("arguments[0].click();", self.element(path))
        self.sleep(sleepafter)

    def jsRemove(self, path: str, sleepafter: float = 0.5):
        self.driver.execute_script("document.querySelector(arguments[0]).remove();", path)
        self.sleep(sleepafter)

    def waitAndClick(self, path: str, sleepafter: float = 0.5):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH if path.startswith(("/", ".//")) else By.CSS_SELECTOR, path))).click()
        self.sleep(sleepafter)

    def zoomOut(self, percentage: int, sleepafter: float = 0.2):
        self.driver.execute_script(f"document.body.style.zoom='{percentage}%'")
        self.sleep(sleepafter)

    def getJlemTimeNow(self):
        return datetime.now(pytz.timezone("Asia/Jerusalem")).isoformat()

    def getRandomHash(self):
        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))

    def printRow(self):
        print(f"{(self.english_title)!s:29.29} - {(self.hebrew_title)!s:20.20} - {(self.release_date)!s:10.10} - {self.CINEMA_NAME!s:12.12} - {self.screening_city!s:15.15} - {self.date_of_showing!s:10.10} - {self.showtime!s:5.5}".rstrip())
