from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class JAFCtheque(BaseCinema):
    CINEMA_NAME = "Jaffa Cinema"
    SCREENING_CITY = "Jaffa"
    URL = "https://www.jaffacinema.com/"

    def logic(self):
        self.sleep(2)

        for hebrew_film_block in range(1, self.lenElements("/html/body/main/div/div[1]/section[2]/div/div/div/div[2]/div/div/div/div") + 1):
            hebrew_title = self.element(f"/html/body/main/div/div[1]/section[2]/div/div/div/div[2]/div/div/div/div[{hebrew_film_block}]/div/div[1]/div/h2").text.strip()
            self.hebrew_titles.append(re.sub(r"[\s\-\u2013\u2014]*(?:(?:eng(?:lish)?|heb(?:rew)?)\s*(?:subs|subtitles)|(?:eng(?:lish)?|heb(?:rew)?)\s*(?:\+|&|/|and)\s*(?:eng(?:lish)?|heb(?:rew)?)\s*(?:subs|subtitles))[\s\-\u2013\u2014]*$", "", hebrew_title, flags=re.I))

        self.driver.get("https://www.jaffacinema.com/en/main/")
        self.sleep(2)
        for film_block in range(1, self.lenElements("/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div") + 1):
            english_title = self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[1]/div/h2").text.strip()
            self.english_title = re.sub(r"[\s\-\u2013\u2014]*(?:(?:eng(?:lish)?|heb(?:rew)?)\s*(?:subs|subtitles)|(?:eng(?:lish)?|heb(?:rew)?)\s*(?:\+|&|/|and)\s*(?:eng(?:lish)?|heb(?:rew)?)\s*(?:subs|subtitles))[\s\-\u2013\u2014]*$", "", english_title, flags=re.I)
            self.hebrew_title = self.hebrew_titles[film_block - 1]

            run_director_info = self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[1]/div/p").text.strip()

            parts = [p.strip() for p in run_director_info.split("|")]
            runtime_part = parts[0]
            director_part = parts[1] if len(parts) > 1 else ""

            if "," in director_part:
                director_part = director_part.split(",")[0].strip()
            minutes, hours = 0, 0
            if "h" in runtime_part.strip():
                hours_str = runtime_part.strip().split("h")[0].strip()
                hours = int(hours_str)
                runtime_part = runtime_part.strip().split("h")[1].strip()
            if "m" in runtime_part.strip():
                minutes_str = runtime_part.strip().replace("m", "").strip()
                minutes = int(minutes_str)

            self.runtime = hours * 60 + minutes
            self.directed_by = director_part

            xpaths = {
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/p[1]": "strip",
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/p[1]/strong": "strip",
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/div/div/div/div/article/div/div/div/div/div/div/p[1]/strong": "strip",
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/article/div/div/div[1]/div/div/div/p[1]": "content",
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/div/div/p[1]/strong": "strip",
                f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[1]/div/div/p[1]": "content",
            }

            for xpath, mode in xpaths.items():
                try:
                    if mode == "strip":
                        release_year = self.element(xpath).text.strip()
                    elif mode == "content":
                        release_year = self.element(xpath).get_attribute("textContent")
                    break
                except:
                    continue

            self.release_year = self.tryExceptNone(lambda: int(re.search(r"\b(\d{4})\b", release_year).group(1)))

            showtime_strings = []
            try:
                showtime_strings.append(self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[2]/p").text.strip())
            except:
                for showdate in range(1, self.lenElements(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[2]/select/option") + 1):
                    showtime_strings.append(self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[2]/select/option[{showdate}]").text.strip())

            crossed_year = False
            trying_year = self.current_year
            for idx, showtime_string in enumerate(showtime_strings):
                left_info, right_info = [p.strip() for p in showtime_string.split(",", 1)]
                dd, mm = [p.strip() for p in left_info.split("/", 1)]
                if self.current_month == "12" and not crossed_year and (str(mm) == "1" or str(mm) == "01"):
                    crossed_year = True
                    trying_year = str(int(trying_year) + 1)
                yyyy = str(trying_year)
                date_of_showing = f"{str(dd)}/{str(mm)}" + f"/{yyyy}"
                self.date_of_showing = datetime.strptime(date_of_showing, "%d/%m/%Y").date().isoformat()
                self.showtime = str(right_info.split(" ")[1])

                self.english_href = self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[2]/a[{idx + 1}]").get_attribute("href")
                self.hebrew_href = self.element(f"/html/body/main/div/div[1]/section[3]/div/div/div/div[2]/div/div/div/div[{film_block}]/div/div[2]/div[2]/a[{idx + 1}]").get_attribute("href")
                self.screening_city = self.SCREENING_CITY
                self.screening_type = "Regular"

                self.appendToGatheringInfo()
