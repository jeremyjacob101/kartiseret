from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class CinemaCity(BaseCinema):
    CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/"

    def getEventId(self, path: str):
        self.driver.execute_script(
            """
                            return (function(node){
                                if (!window.ko) return null;
                                var data = ko.dataFor(node) || {};
                                var h2 = (data.selected && typeof data.selected.hour2 === "function" && data.selected.hour2())
                                        || (data.selected && typeof data.selected.hour === "function" && data.selected.hour());
                                return h2 && (h2.EventId || h2.EventID || h2.EventID1) || null;
                            })(arguments[0]);
                            """,
            self.element(path),
        )

    def logic(self):
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('body > flashy-popup');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#popupVSChat');if(el){el.remove();}")
        self.sleep(3)
        self.zoomOut(50)

        for _ in range(8):
            element = self.element("#change-bg > div.container.movies.index-movies-mob > div.movie-more-wrapper > div.row > div > p > a")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.sleep(1)
            try:
                element.click()
                self.sleep(3)
            except:
                break

        for cinema_block in range(1, self.lenElements("#moviesContainer > div", "row mainThumbWrapper") + 1):
            for film_card in range(1, self.lenElements(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div") + 1):
                self.trying_names.append(self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/p[1]").get_attribute("textContent"))

                rating = self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[4]/span").get_attribute("textContent")
                if rating == "מותר לכל":
                    rating = "All"
                if rating == "הותר מגיל 16":
                    rating = "16+"
                if rating == "הותר מגיל 14":
                    rating = "14+"
                if rating == "הותר מגיל 12":
                    rating = "12+"
                if rating == "טרם נקבע" or rating == "" or not rating:
                    rating = None
                self.ratings.append(rating)

                try_this_hebrew_name = self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/h4").get_attribute("textContent")
                if "מדובב לרוסית-" in try_this_hebrew_name:
                    self.dub_languages.append("Russian")
                    try_this_hebrew_name = re.sub(r"\s*[–—-]?\s*מדובב לרוסית\s*[–—-]?\s*", " ", try_this_hebrew_name)
                elif "מדובב לצרפתית-" in try_this_hebrew_name:
                    self.dub_languages.append("French")
                    try_this_hebrew_name = re.sub(r"\s*[–—-]?\s*מדובב לצרפתית\s*[–—-]?\s*", " ", try_this_hebrew_name)
                elif "מדובב-" in try_this_hebrew_name:
                    self.dub_languages.append("English")
                    try_this_hebrew_name = re.sub(r"\s*[–—-]?\s*מדובב\s*[–—-]?\s*", " ", try_this_hebrew_name)
                self.trying_hebrew_names.append(try_this_hebrew_name)

        self.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")

        self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dt/a")
        for cinema in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li") + 1):
            self.screening_city = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a/span").get_attribute("textContent")
            self.screening_type = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a/span").get_attribute("textContent")

            self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a")
            self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dt/a")
            for day in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li") + 1):
                self.date_of_showing = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a").get_attribute("textContent")
                self.date_of_showing = datetime.strptime(re.search(r"\d{1,2}/\d{1,2}/\d{4}", self.date_of_showing).group(), "%d/%m/%Y").date().isoformat()

                self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a")
                self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dt/a")
                name_to_idx = {str(name).lower(): i for i, name in enumerate(self.trying_hebrew_names)}
                for film_index in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li") + 1):
                    checking_film_name = str(self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{film_index}]/a").get_attribute("textContent")).lower()
                    checking_film = name_to_idx.get(checking_film_name)
                    if checking_film is None:
                        continue

                    self.english_title = self.trying_names[checking_film]
                    self.hebrew_title = self.trying_hebrew_names[checking_film]
                    self.rating = self.ratings[checking_film]

                    self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{film_index}]/a")
                    self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dt/a")
                    for time in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li") + 1):
                        self.showtime = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a").get_attribute("textContent")

                        self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a")
                        event_id = self.getEventId("/html/body/div[4]/div[2]/div/div/div[2]/div/div[6]/button")
                        self.english_href = f"https://tickets.cinema-city.co.il/order/{event_id}?lang=en"
                        self.hebrew_href = f"https://tickets.cinema-city.co.il/order/{event_id}?lang=he"

                        self.appendToGatheringInfo()
                        self.printShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
