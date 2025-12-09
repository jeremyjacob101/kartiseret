from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HERZtheque(BaseCinema):
    CINEMA_NAME = "Herziliya Cinematheque"
    SCREENING_CITY = "Herziliya"
    URL = "https://www.hcinema.org.il/"

    def logic(self):
        self.sleep(2)

        for film_card in range(1, self.lenElements("/html/body/main/div/div/div[3]/div/div/div/div/div/div/div[2]/div/div") + 1):
            try:
                real_card_check = self.element(f"/html/body/main/div/div/div[3]/div/div/div/div/div/div/div[2]/div/div[{film_card}]/div/div/div[2]/div[2]/div/div/div/a/span").text.strip()
                if real_card_check != "מידע נוסף":
                    raise
            except:
                continue
            print(f"film_card: {film_card}")
            self.hebrew_hrefs.append(self.element(f"/html/body/main/div/div/div[3]/div/div/div/div/div/div/div[2]/div/div[{film_card}]/div/div/div[2]/div[2]/div/div/div/a").get_attribute("href"))
            full_info = self.element(f"/html/body/main/div/div/div[3]/div/div/div/div/div/div/div[2]/div/div[{film_card}]/div/div/div[2]/div[1]/div[2]/div/div/div/div").text.strip()
            date_part, time_part = full_info.split(" ", 1)
            self.date_of_showings.append(date_part)
            self.showtimes.append(time_part)

        for idx, href in enumerate(self.hebrew_hrefs):
            self.driver.get(href)
            self.sleep(0.2)

            self.english_title = self.element("/html/body/div[2]/div/div/div[1]/div[2]/div/h3").text.strip()
            self.hebrew_title = self.element("/html/body/div[2]/div/div/div[1]/div[1]/div/h1").text.strip()
            if "(שלישי זהב)" in self.hebrew_title:
                self.hebrew_title = str(self.hebrew_title.replace("(שלישי זהב)", "").strip())
            if "(ללא תשלום למנויים)" in self.hebrew_title:
                self.hebrew_title = str(self.hebrew_title.replace("(ללא תשלום למנויים)", "").strip())
            if "(ללא תוספת למנויים)" in self.hebrew_title:
                self.hebrew_title = str(self.hebrew_title.replace("(ללא תוספת למנויים)", "").strip())
            if "+ הרצאה" in self.hebrew_title:
                self.hebrew_title = str(self.hebrew_title.split("+ הרצאה")[0].strip())
            if "+ שיחה" in self.hebrew_title:
                self.hebrew_title = str(self.hebrew_title.split("+ שיחה")[0].strip())
            dub_check = self.element("/html/body/div[2]/div/div/div[1]/div[4]/div/div/div/p").text
            if "דיבוב עברי" in dub_check or "דיבוב" in self.hebrew_title:
                self.dub_language = "Hebrew"
            else:
                self.dub_language = None

            release_year = re.search(r"\b(\d{4})\b", self.element("/html/body/div[2]/div/div/div[1]/div[3]/div/h3").text.strip())
            if release_year:
                self.release_year = release_year.group(1)
            runtime = re.search(r"(\d+)\s*דק׳", self.element("/html/body/div[2]/div/div/div[1]/div[4]/div/div/div/p").text)
            if runtime:
                self.runtime = int(runtime.group(1))

            self.date_of_showing = datetime.strptime(self.date_of_showings[idx], "%d/%m/%Y").date().isoformat()
            self.showtime = self.showtimes[idx]

            self.hebrew_href = self.element(f"/html/body/div[2]/div/div/div[1]/div[6]/div/div/a").get_attribute("href")
            self.english_href = self.hebrew_href

            self.screening_type = "Regular"
            self.screening_city = self.SCREENING_CITY

            self.printRow()
            # self.appendToGatheringInfo()
