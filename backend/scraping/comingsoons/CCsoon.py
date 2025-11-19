from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class CCsoon(BaseCinema):
    CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/comingsoon"

    def logic(self):
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('body > flashy-popup');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#popupVSChat');if(el){el.remove();}")
        self.sleep(5)
        self.zoomOut(50)

        for _ in range(10):
            element = self.element("#change-bg > div > div > div > div.movies.row > div > p > a")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.sleep(1)
            try:
                element.click()
                self.sleep(3)
            except:
                break

        for cinema_block in range(1, self.lenElements("#moviesContainer > div", "row mainThumbWrapper") + 1):
            for film_card in range(1, self.lenElements(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div") + 1):
                self.hebrew_title = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[1]/div/h2").get_attribute("textContent").strip()
                if "מדובב לרוסית" in self.hebrew_title or "בתרגום לרוסית" in self.hebrew_title or "מדובב לצרפתית" in self.hebrew_title or "בתרגום לצרפתית" in self.hebrew_title or "מדובב" in self.hebrew_title or "HFR" in self.hebrew_title:
                    continue
                elif "תלת מימד" in self.hebrew_title:
                    self.hebrew_title = re.sub(r"\s*[-–—־]?\s*תלת מימד\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                elif "אנגלית" in self.hebrew_title:
                    self.hebrew_title = re.sub(r"\s*[-–—־]?\s*אנגלית\s*[-–—־]?\s*", "", self.hebrew_title).strip()

                self.english_title = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/p[1]").get_attribute("textContent").strip()
                if self.english_title == "" or self.english_title == None:
                    self.english_title = self.hebrew_title

                self.runtime = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[2]/span").get_attribute("textContent").strip()
                self.rating = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[4]/span").get_attribute("textContent").strip()

                release_date = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[3]/span").get_attribute("textContent").strip()
                self.release_date = datetime.strptime(release_date, "%d/%m/%Y").date().isoformat()

                self.helper_id = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/ul/li[1]/a").get_attribute("href")
                self.helper_type = "href"

                self.appendToGatheringInfo()
