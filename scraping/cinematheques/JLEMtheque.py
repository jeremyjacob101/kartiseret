from scraping.BaseCinema import BaseCinema

from datetime import datetime
import re

from selenium.webdriver.common.by import By


class JLEMtheque(BaseCinema):
    CINEMA_NAME = "JLMCT"
    SCREENING_CITY = "Jerusalem"
    URL = "https://jer-cin.org.il/en/article/4284"

    def logic(self):
        self.sleep(3)

        for _ in range(1, 46):
            date_of_showing = self.element("/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[1]/p").text.strip().split("|")[1].strip()
            self.date_of_showing = datetime.strptime(date_of_showing, "%d.%m.%y").date().isoformat()
            for film_block in range(2, self.lenElements("/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div", "lobby-container") + 2):
                try:
                    no_screenings_check = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[3]/div[1]/a").text.strip()
                    if "No Screenings" in no_screenings_check:
                        continue
                except:
                    pass
                try:
                    try:
                        self.english_title = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[3]/div[3]/a").text.strip()
                    except:
                        self.english_title = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[3]/div[3]").text.strip()
                    self.showtime = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[1]/div/div[1]").text.strip()
                    self.directed_by = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[3]/div[4]/span[1]").text.strip().split(":")[1].strip()
                    self.runtime = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[3]/div[4]/span[2]").text.strip().split(" ")[0].strip()
                    try:
                        self.english_href = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[1]/div/div[3]/div/div/div/div/button").get_attribute("data-url")
                    except:
                        self.english_href = self.element(f"/html/body/div[4]/div/div[2]/div[2]/div/div/div[4]/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div[{film_block}]/div[2]/div[1]/a").get_attribute("href")
                    self.screening_city = self.SCREENING_CITY
                    self.screening_type = "Regular"
                except:
                    continue

                self.appendToGatheringInfo()

            self.element("#calender-filter > p.active").find_element(By.XPATH, "following-sibling::p").click()
            self.sleep(1)

        URL_2 = "https://jer-cin.org.il/he/article/4285"
