from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HCsoon(BaseCinema):
    CINEMA_NAME = "Hot Cinema"
    URL = "https://hotcinema.co.il/ComingSoon"

    def logic(self):
        self.sleep(3)
        try:
            self.waitAndClick("/html/body/div[7]/div/button", 3)
        except:
            self.tryExceptPass(lambda: self.waitAndClick("/html/body/div[7]/div/div/button", 3))
        self.waitAndClick("/html/body/div[3]/div/div/div[1]/a", 3)
        self.zoomOut(50)

        self.tryExceptPass(lambda: self.driver.execute_script("document.querySelector('.pp-backdrop').remove();"))
        self.tryExceptPass(lambda: self.driver.execute_script("document.querySelector('.pp-backdrop').style.display='none';"))

        for film_block in range(2, self.lenElements("/html/body/div[2]/div[4]/div[2]/div/div/div") + 1, 2):
            for film_card in range(1, self.lenElements(f"/html/body/div[2]/div[4]/div[2]/div/div/div[{film_block}]/div/h4")):
                self.english_hrefs.append(self.element(f"/html/body/div[2]/div[4]/div[2]/div/div/div[{film_block}]/div[{film_card}]/div[1]/a").get_attribute("href"))
        for href in self.english_hrefs:
            self.driver.get(href)
            self.sleep(0.25)

            self.english_title = self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/h2").text.strip()
            self.hebrew_title = self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/h1").text.strip()

            if "סטנדאפ" in self.english_title or "סטנדאפ" in self.hebrew_title or "מדובב לרוסית" in self.hebrew_title or "מדובב לעברית" in self.hebrew_title or "מדובב לצרפתית" in self.hebrew_title or "סינימה אישי" in self.hebrew_title or "קומדי בר" in self.hebrew_title or "HFR" in self.hebrew_title or "תלת-ממד" in self.hebrew_title:
                continue

            self.hebrew_title = re.sub(r"^\s*סינמה נוסטלגיה\s*[-–—]\s*", "", self.hebrew_title).strip()
            self.hebrew_title = re.sub(r"^\s*סינמה נוסטלגי\s*[-–—]\s*", "", self.hebrew_title).strip()
            self.hebrew_title = re.sub(r"\s*אנגלית\s*$", "", self.hebrew_title).strip()

            raw_text = (self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]").text or "").strip()
            last_token = raw_text.split()[-1] if raw_text else ""
            self.release_year = int(last_token) if last_token.isdigit() and len(last_token) == 4 else None

            self.ratings = self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[2]/div[2]/span").text.strip()
            self.runtime = self.tryExceptNone(lambda: int(re.sub(r"\D", "", self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/span").text.strip())))

            release_date = self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[2]/div[1]/span").text.split(":")[1].strip().replace(".", "/")
            self.release_date = datetime.strptime(release_date, "%d/%m/%Y").date().isoformat()

            self.appendToGatheringInfo()
