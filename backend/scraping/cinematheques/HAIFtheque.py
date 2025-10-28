from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HAIFtheque(BaseCinema):
    CINEMA_NAME = "Haifa Cinematheque"
    SCREENING_CITY = "Haifa"
    URL = "https://www.haifacin.co.il/Events/trom/%D7%AA%D7%95%D7%9B%D7%A0%D7%99%D7%AA_%D7%94%D7%97%D7%95%D7%93%D7%A9"

    def logic(self):
        self.sleep(2)

        for film_card in range(1, self.lenElements("/html/body/section[2]/div[1]/div[1]/div")):
            self.hebrew_hrefs.append(self.element(f"/html/body/section[2]/div[1]/div[1]/div[{film_card}]/div/div[2]/a[1]").get_attribute("href"))
        for href in self.hebrew_hrefs:
            self.driver.get(href)
            self.sleep(0.25)
            self.english_title = self.element(f"/html/body/div[4]/section[2]/div[2]/div/div/div[2]").text.strip()
            self.hebrew_title = self.element(f"/html/body/div[4]/section[2]/div[2]/div/div/h1").text.strip()
            self.english_href = self.element(f"/html/body/div[4]/section[2]/div[2]/div/div/a").get_attribute("href")
            self.hebrew_href = self.english_href
            self.showtime = self.element(f"/html/body/div[4]/section[4]/div[3]").text.strip()
            date_of_showing = self.element(f"/html/body/div[4]/section[4]/div[2]").text.strip().split(",")[1].strip()
            self.date_of_showing = datetime.strptime(date_of_showing, "%d.%m.%y").date().isoformat()
            self.screening_city = self.SCREENING_CITY
            self.screening_type = "Regular"
            try:
                release_year = self.element("/html/body/div[4]/section[5]/div[1]/strong[1]").text.strip()
            except:
                continue

            self.release_year = self.tryExceptNone(lambda: int(re.search(r"\b(\d{4})\b", release_year).group(1)))

            self.appendToGatheringInfo()
