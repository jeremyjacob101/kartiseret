from scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class HERZtheque(BaseCinema):
    CINEMA_NAME = "Herziliya Cinematheque"
    SCREENING_CITY = "Herziliya"
    URL = "https://hcinema.smarticket.co.il/"

    month_mapping = {"ינואר": "01", "פברואר": "02", "מרץ": "03", "אפריל": "04", "מאי": "05", "יוני": "06", "יולי": "07", "אוגוסט": "08", "ספטמבר": "09", "אוקטובר": "10", "נובמבר": "11", "דצמבר": "12"}

    def logic(self):
        self.sleep(2)

        crossed_year = False
        trying_year = self.current_year
        for film_card in range(1, self.lenElements("/html/body/main/section[1]/div/div")):
            full_title = self.element(f"/html/body/main/section[1]/div/div[{film_card}]/a/div[2]/div[1]").text.strip()
            try:
                self.english_title = str(full_title.split("-")[1].strip().removeprefix("!"))
            except:
                continue
            if "(שלישי זהב)" in self.english_title:
                self.english_title = str(self.english_title.replace("(שלישי זהב)", "").strip())
            if "(ללא תשלום למנויים)" in self.english_title:
                self.english_title = str(self.english_title.replace("(ללא תשלום למנויים)", "").strip())
            if "(ללא תוספת למנויים)" in self.english_title:
                self.english_title = str(self.english_title.replace("(ללא תוספת למנויים)", "").strip())
            if "+ הרצאה" in self.english_title:
                self.english_title = str(self.english_title.split("+ הרצאה")[0].strip())
            if "+ שיחה" in self.english_title:
                self.english_title = str(self.english_title.split("+ שיחה")[0].strip())
            self.hebrew_title = str(full_title.split("-")[0].strip())
            try:
                if "דיבוב" in full_title.split("-")[2]:
                    self.dub_language = "Hebrew"
                else:
                    self.dub_language = "None"
            except:
                self.dub_language = None

            dd = str(self.element(f"/html/body/main/section[1]/div/div[{film_card}]/a/div[1]/span").text.strip().split("\n")[0].strip())
            mm = self.month_mapping[self.element(f"/html/body/main/section[1]/div/div[{film_card}]/a/div[1]/span/span").text.strip()]
            mm = self.month_mapping.get(mm, mm)
            if self.current_month == "12" and not crossed_year and (str(mm) == "01"):
                crossed_year = True
                trying_year = str(int(trying_year) + 1)
            date_of_showing = f"{dd}/{mm}/{trying_year}"
            self.date_of_showing = datetime.strptime(date_of_showing, "%d/%m/%Y").date().isoformat()

            try:
                date_info_1 = self.element(f"/html/body/main/section[1]/div/div[{film_card}]/a/div[2]/div[5]/div[2]/span[2]").text.strip()
            except:
                date_info_1 = ""
            try:
                date_info_2 = self.element(f"/html/body/main/section[1]/div/div[{film_card}]/a/div[2]/div[5]/div").text.strip().split(",", 1)[-1].strip()
            except:
                date_info_2 = ""
            pat = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
            times = max((pat.findall(date_info_1), pat.findall(date_info_2)), key=len)
            start_s, end_s = times
            h1, m1 = map(int, start_s.split(":"))
            h2, m2 = map(int, end_s.split(":"))
            self.showtime = f"{h1:02d}:{m1:02d}"
            self.runtime = ((h2 * 60 + m2) - (h1 * 60 + m1)) % (24 * 60)

            self.screening_type = "Regular"
            self.screening_city = self.SCREENING_CITY

            self.appendToGatheringInfo(True)
