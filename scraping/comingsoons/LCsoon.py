from scraping.comingsoons.BaseSoon import BaseSoon

from datetime import datetime
import re


class LCsoon(BaseSoon):
    CINEMA_NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        self.sleep(3)
        self.jsClick("/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/ul/li[2]")
        for film_card in range(1, self.lenElements("/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li")):
            self.english_hrefs.append(self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li[{film_card}]/div/a[1]").get_attribute("href"))

            release_date = self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li[{film_card}]/div/a[1]/div/div[2]").text
            if release_date is not None and release_date != "":
                release_date = release_date.split(":", 1)[1].strip()
                self.release_dates.append(datetime.strptime(release_date, "%d/%m/%Y").date().isoformat())

        for idx, href in enumerate(self.english_hrefs):
            hebrew_href = str(href).replace("/en", "")
            self.driver.get(hebrew_href)
            self.sleep(0.5)

            self.hebrew_title = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text.strip()

            self.driver.get(href)
            self.sleep(0.5)

            self.release_date = self.release_dates[idx]

            self.english_title = str(self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[1]/h1").text)
            if "dubbed" in self.english_title.lower():
                self.english_title = re.sub(r"\b[dD]ubbed\b", "", self.english_title).strip()
                self.hebrew_title = self.hebrew_title.replace("מדובב", "").strip()
            if "dubbded" in self.english_title.lower():
                self.english_title = re.sub(r"\b[dD]ubbded\b", "", self.english_title).strip()
                self.hebrew_title = self.hebrew_title.replace("מדובב", "").strip()

            self.release_year = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]").text
            self.release_year = int(m.group(0)) if (m := re.search(r"\b(19|20)\d{2}\b", self.release_year)) else None

            self.original_language = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]").text
            self.original_language = str(m.group(1)) if (m := re.search(r"^\s*([A-Za-z]+)", self.original_language)) else "Hebrew"

            self.rating = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[3]").text
            self.rating = str(self.rating.split(":", 1)[1].strip()) if self.rating else "All"

            runtime = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[3]").text
            if runtime and runtime.isdigit():
                self.runtime = runtime

            self.helper_id = href
            self.helper_type = "href"

            self.appendToGatheringInfo()
            # self.printComingSoon()
