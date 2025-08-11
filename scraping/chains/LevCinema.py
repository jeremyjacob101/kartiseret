from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class LevCinema(BaseCinema):
    CINEMA_NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        print(f"scraping lev cinema")

        for tab_view in (1, 2):
            for i in range(1, self.elements(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li", "featureItem") + 1):
                name = self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li[{i}]/div/a[1]/img").get_attribute("alt")
                href = self.element(f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab_view}]/div/ul/li[{i}]/div/a[1]").get_attribute("href")
                self.trying_names.append(name)
                self.trying_hrefs.append(href)

        for film, href in enumerate(self.trying_hrefs):
            self.driver.get(self.trying_hrefs[film])

            title = self.trying_names[film]

            release_year = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]").text
            release_year = int(m.group(0)) if (m := re.search(r"\b(19|20)\d{2}\b", release_year)) else None

            audio_language = self.element("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]").text
            audio_language = str(m.group(1)) if (m := re.search(r"^\s*([A-Za-z]+)", audio_language)) else ""

            for city in range(1, self.elements("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div") + 1):
                screening_city = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/h3").text
                for day in range(1, self.elements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div") + 1):
                    date_of_showing = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/span").text
                    date_of_showing = re.search(r"\d{1,2}/\d{1,2}", date_of_showing).group(0)
                    date_of_showing = datetime.strptime(f"2025/{date_of_showing}", "%Y/%d/%m")
                    date_of_showing = str(date_of_showing.date().isoformat())
                    for time in range(1, self.elements(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div") + 1):
                        showtime = str(self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").text)
                        showtime_href = self.element(f"/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[6]/div[{city}]/div[{day}]/div[{time}]/a").get_attribute("href")

                        data_to_push = {
                            "showtime_id": self.getRandomHash(),
                            "title": title,
                            "cinema": self.CINEMA_NAME,
                            "year": release_year,
                            "audio": audio_language,
                            "href": showtime_href,
                            "city": screening_city,
                            "date": date_of_showing,
                            "time": showtime,
                            "created_at": self.getJlemTimeNow(),
                        }

                        print(f"{str(self.getRandomHash()):15} - {str(title):24} - {str(self.CINEMA_NAME):12} - {str(release_year):4} - {str(audio_language):10} - {str(showtime_href):.20} - {str(screening_city):15} - {str(date_of_showing):10} - {str(showtime):5} - {str(self.getJlemTimeNow()):.10}")
                        self.supabase.table("testingMovies").insert(data_to_push).execute()
