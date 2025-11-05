from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HOLONtheque(BaseCinema):
    CINEMA_NAME = "Holon Cinematheque"
    SCREENING_CITY = "Holon"
    URL = "https://www.cinemaholon.org.il/screening-and-events/"

    def logic(self):
        self.sleep(3)

        for _ in range(1, 6):
            for film_block in range(1, self.lenElements("/html/body/div[5]/div[4]/section[2]/div/div/div/div/div") + 1):
                try:
                    self.element(f"/html/body/div[5]/div[4]/section[2]/div/div/div/div/div[{film_block}]/div[2]")
                except:
                    continue
                for film_card in range(1, self.lenElements(f"/html/body/div[5]/div[4]/section[2]/div/div/div/div/div[{film_block}]/div[2]/div/div") + 1):
                    self.hebrew_hrefs.append(self.element(f"/html/body/div[5]/div[4]/section[2]/div/div/div/div/div[{film_block}]/div[2]/div/div[{film_card}]/div/a[2]").get_attribute("href"))
            self.click("/html/body/div[5]/div[4]/section[1]/div/div/div[2]/div/button[2]", 2)
        self.hebrew_hrefs = list(dict.fromkeys(self.hebrew_hrefs))

        for href in self.hebrew_hrefs:
            self.driver.get(href)
            self.zoomOut(50)

            self.hebrew_title = self.element("/html/body/div[5]/div[1]/div/h1").text.strip()
            if self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2") == 3:
                self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2[3]/b").text.strip()
            elif self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2") == 2:
                try:
                    self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/p[1]/strong").text.strip()
                except:
                    try:
                        self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2[2]/b").text.strip()
                    except:
                        self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2[2]").text.strip()
            elif self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2") == 1:
                if self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2/b") == 6 or self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2/b") == 5:
                    self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2/b[5]").text.strip()
                else:
                    self.english_title = self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/div/h2/b[4]").text.strip()
            else:
                self.english_title = self.hebrew_title

            self.runtime = self.tryExceptNone(lambda: int(re.findall(r"\d+", self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/ul/li[1]/span").text)[-1]))
            self.release_year = self.tryExceptNone(lambda: re.search(r"\b\d{4}\b", self.element("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/ul/li[2]/span").text.strip()).group(0))

            self.click("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[1]/div[1]", 1)
            for showdate in range(1, self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[1]/div[2]/div/div") + 1):
                self.click("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[1]/div[1]", 1)
                date_of_showing = self.element(f"/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[1]/div[2]/div/div[{showdate}]").text.strip()
                self.date_of_showing = datetime.strptime(date_of_showing, "%d/%m/%y").date().isoformat()
                self.click(f"/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[1]/div[2]/div/div[{showdate}]", 1)

                self.click("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[2]/div/div/div[1]", 1)
                for showtime in range(1, self.lenElements("/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[2]/div/div/div[2]/div/div") + 1):
                    self.showtime = self.element((f"/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[2]/div/div/div[2]/div/div[{showtime}]")).text.strip()
                    self.hebrew_href = self.element(f"/html/body/div[5]/div[3]/section[1]/div/div/div[2]/div/form/div[2]/div/div/div[2]/div/div[{showtime}]").get_attribute("data-value")
                    self.english_href = self.hebrew_href
                    self.screening_city = self.SCREENING_CITY
                    self.screening_type = "Regular"

                    self.appendToGatheringInfo()
