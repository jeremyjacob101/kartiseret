from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class MLsoon(BaseCinema):
    CINEMA_NAME = "MovieLand"
    URL = "https://www.movieland.co.il/soon"

    def logic(self):
        self.sleep(8)
        self.tryExceptPass(lambda: self.waitAndClick("#sbuzz-confirm", 2))
        self.tryExceptPass(lambda: self.waitAndClick("#gdpr-module-message > div > div > div.gdpr-content-part.gdpr-accept > a", 2))

        self.waitAndClick("#chooseTheaterModalCenter > div > div > a", 5)
        self.sleep(2)

        for film_card in range(1, self.lenElements("/html/body/div[1]/div[10]/div[2]/div/div/div") + 1):
            self.english_hrefs.append(self.element(f"/html/body/div[1]/div[10]/div[2]/div/div/div[{film_card}]/div/div/div/div[1]/a[1]").get_attribute("href"))
        for href in self.english_hrefs:
            self.driver.get(href)
            self.sleep(0.5)

            if "IsLtr" in self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[1]").get_attribute("className"):
                continue

            self.hebrew_title = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[1]").text.strip()
            if "(מדובב)" in self.hebrew_title:
                continue
            if "3D" in self.hebrew_title:
                self.hebrew_title = self.hebrew_title.replace("3D", "").strip()
            if "HFR" in self.hebrew_title:
                self.hebrew_title = self.hebrew_title.replace("HFR", "").strip()
            if "תלת מימד" in self.hebrew_title:
                self.hebrew_title = self.hebrew_title.replace("תלת מימד", "").strip()

            self.english_title = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[2]").text.strip()
            if "3D" in self.english_title:
                self.english_title = self.english_title.replace("3D", "").strip()
            if "HFR" in self.english_title:
                self.english_title = self.english_title.replace("HFR", "").strip()
            if not self.english_title:
                self.english_title = self.hebrew_title

            release_date = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[4]").text.strip()
            self.release_date = datetime.strptime(release_date, "%d/%m/%Y").date().isoformat()

            self.rating = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[10]").text.strip()
            runtime = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[13]").text.strip()
            runtime = re.sub(r"\D", "", runtime)
            if runtime and runtime.isdigit():
                self.runtime = runtime

            release_year = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[15]").text.strip()
            if release_year and release_year.isdigit():
                self.release_year = release_year
            original_language = self.element("/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[16]").text.strip()
            if original_language != "יעודכן בקרוב":
                self.original_language = original_language.split(":", 1)[1].strip()

            self.appendToGatheringInfo()
