from scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class SSCtheque(BaseCinema):
    CINEMA_NAME = "Sam Spiegel Cinema"
    SCREENING_CITY = "Jerusalem"
    URL = "https://cinema.jsfs.co.il/%d7%9c%d7%95%d7%97-%d7%94%d7%a7%d7%a8%d7%a0%d7%95%d7%aa/"

    def logic(self):
        self.sleep(1)
        self.english_href = self.URL
        self.hebrew_href = self.URL

        crossed_year = False
        trying_year = self.current_year
        for film_card in range(1, self.lenElements("/html/body/div[2]/div[3]/div/div/div/div/div") + 1):
            full_title = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div/div/h1").text.strip()
            title_parts = [part.strip() for part in full_title.split("|")]
            if len(title_parts) >= 3:
                self.hebrew_title, self.english_title = title_parts[0], title_parts[2]
            elif len(title_parts) == 2:
                self.hebrew_title, self.english_title = title_parts[0], title_parts[1]
            else:
                continue

            date_of_showing = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div[2]/div/h2").text.strip()
            month_of_showing = date_of_showing.split("/")[1].strip()
            if self.current_month == "12" and not crossed_year and (str(month_of_showing) == "1" or str(month_of_showing) == "01"):
                crossed_year = True
                trying_year = str(int(trying_year) + 1)
            yyyy = str(trying_year)
            date_of_showing = date_of_showing + f"/{yyyy}"
            self.date_of_showing = datetime.strptime(date_of_showing, "%d/%m/%Y").date().isoformat()

            self.showtime = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div[3]/div/h2").text.strip()

            num_text_blocks = self.lenElements(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p")
            if num_text_blocks == 1:
                if "|" in self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p").get_attribute("textContent").split("\n")[0].strip():
                    full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p").get_attribute("textContent").split("\n")[0].strip()
                elif "|" in self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p").get_attribute("textContent").split("\n")[1].strip():
                    full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p").get_attribute("textContent").split("\n")[1].strip()
            elif num_text_blocks >= 2:
                if "|" in self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p[1]").get_attribute("textContent").split("\n")[0].strip():
                    full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p[1]").get_attribute("textContent").split("\n")[0].strip()
                else:
                    try:
                        full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p[2]/span").get_attribute("textContent").split("\n")[1].strip()
                    except:
                        try:
                            full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[4]/div/p[2]").get_attribute("textContent").split("\n")[1].strip()
                        except:
                            full_info = self.element(f"/html/body/div[2]/div[3]/div/div/div/div/div[{film_card}]/div/div[5]/div/p[2]/span").get_attribute("textContent").split("\n")[1].strip()

            info_parts = [part.strip() for part in full_info.split("|")]
            for part in info_parts:
                if "דקות" in part:
                    match = re.search(r"\d+", part)
                    if match:
                        self.runtime = int(match.group())
                elif re.fullmatch(r"\d{4}", part):
                    self.release_year = part

            self.screening_city = self.SCREENING_CITY
            self.screening_type = "Regular"

            self.appendToGatheringInfo()
