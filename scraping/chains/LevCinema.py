from scraping.chains.BaseCinema import BaseCinema
import re


class LevCinema(BaseCinema):
    NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        print(f"scraping lev cinema")

        for tab_view in (1, 2):
            for i in range(1, self.elements(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li", "featureItem") + 1):
                name = self.element(f"{f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li"}[{i}]/div/a[1]/img").get_attribute("alt")
                href = self.element(f"{f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li"}[{i}]/div/a[1]").get_attribute("href")
                self.trying_names.append(name)
                self.trying_hrefs.append(href)

        for film, href in enumerate(self.trying_hrefs):
            self.driver.get(self.trying_hrefs[film])

            release_year = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]").text
            release_year = m.group(0) if (m := re.search(r"\b(19|20)\d{2}\b", release_year)) else ""

            audio_language = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]").text
            audio_language = m.group(1) if (m := re.search(r"^\s*([A-Za-z]+)", audio_language)) else ""

            for city in range(1, self.elements("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div") + 1):
                screening_city = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/h3").text
                for day in range(1, self.elements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div") + 1):
                    date_of_showing = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/span").text
                    date_of_showing = m.group(1) if (m := re.search(r"^\s*(\d{1,2}/\d{1,2})", date_of_showing)) else ""
                    for time in range(1, self.elements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div") + 1):
                        showtime = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").text
                        print(f"{self.trying_names[film]:30} - {release_year:12} - {audio_language:10} - {screening_city:15} - {date_of_showing:12} - {showtime:5}")
