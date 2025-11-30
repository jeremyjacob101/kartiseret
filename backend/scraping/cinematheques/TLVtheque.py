from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime, timedelta
import re


class TLVtheque(BaseCinema):
    CINEMA_NAME = "Tel Aviv Cinematheque"
    SCREENING_CITY = "Tel Aviv"
    URL = "https://www.cinema.co.il/en/shown/"

    def logic(self):
        self.sleep(3)

        for i in range(60):
            current_date = self.today_date + timedelta(days=i)
            date_string = current_date.strftime("%Y-%m-%d")
            self.driver.get(f"https://www.cinema.co.il/en/shown/?date={date_string}")
            self.zoomOut(50, 2)
            try:
                print("clicked 1")
                self.driver.execute_script("arguments[0].remove();", self.element("/html/body/div[5]/div[1]/div[2]/div[4]/div/div[1]"))
            except:
                print("clicked 2")
                self.driver.execute_script("arguments[0].remove();", self.element("/html/body/div[3]/div[1]/div[2]/div[4]/div/div[1]"))
            self.sleep(1)

            for film_block in range(1, self.lenElements("/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div") + 1):
                for film_card in range(1, self.lenElements(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div") + 1):
                    self.release_year, self.runtime = None, None

                    self.english_title = self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[1]/h3/a").text.strip()
                    if not re.search(r"[A-Za-z]", self.english_title):
                        fallback_text = self.tryExceptNone(lambda: " ".join(self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[2]/p").get_attribute("textContent").split()[:50]))
                        if fallback_text:
                            words = fallback_text.split()
                            english_words = []
                            for word in words:
                                if re.search(r"[A-Za-z]", word):
                                    english_words.append(word)
                                elif english_words and re.fullmatch(r"[\u2010\u2011\u2012\u2013\u2014\u2212-]+", word):
                                    english_words.append(word)
                                elif english_words:
                                    break
                            self.english_title = " ".join(english_words) if english_words else None

                    trying_year_1 = self.tryExceptNone(lambda: self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[1]/p").get_attribute("textContent"))
                    trying_year_2 = self.tryExceptNone(lambda: " ".join(self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[2]/p").get_attribute("textContent").split()[:50]))
                    for candidate in (trying_year_1, trying_year_2):
                        if candidate:
                            match = re.search(r"\b\d{4}\b", candidate)
                            if match:
                                self.release_year = match.group(0)
                                break

                    trying_runtime_1 = self.tryExceptNone(lambda: self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[1]/p").get_attribute("textContent"))
                    trying_runtime_2 = self.tryExceptNone(lambda: " ".join(self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[2]/p").get_attribute("textContent").split()[:50]))
                    if trying_runtime_1 and "Length:" in trying_runtime_1:
                        match = re.search(r"Length:\s*(\d+)", trying_runtime_1)
                        if match:
                            self.runtime = match.group(1)
                    if not self.runtime and trying_runtime_2 and "דקות" in trying_runtime_2:
                        match = re.search(r"(\d+)\s+דקות", trying_runtime_2)
                        if match:
                            self.runtime = match.group(1)

                    self.date_of_showing = datetime.strptime(date_string, "%Y-%m-%d").date().isoformat()
                    self.english_href = self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[3]/div[1]/a").get_attribute("href")
                    self.hebrew_href = self.english_href.replace("lang=en", "lang=he")
                    self.showtime = self.element(f"/html/body/div[5]/div[1]/div[2]/div[4]/div/div/div/div[2]/div[{film_block}]/div[{film_card}]/div[2]/div[3]/div[1]/a/span").text.strip()
                    self.screening_city = self.SCREENING_CITY
                    self.screening_type = "Regular"

                    self.appendToGatheringInfo()
