from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class CinemaCity(BaseCinema):
    CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/"

    def logic(self):
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('body > flashy-popup');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#popupVSChat');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#gdpr-module-message');if(el){el.remove();}")
        self.sleep(5)
        self.zoomOut(50)

        for _ in range(8):
            scroll_button = self.element("#change-bg > div.container.movies.index-movies-mob > div.movie-more-wrapper > div.row > div > p > a")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", scroll_button)
            self.sleep(1)
            try:
                scroll_button.click()
                self.sleep(3)
            except:
                break

        for cinema_block in range(1, self.lenElements("#moviesContainer > div", "row mainThumbWrapper") + 1):
            for film_card in range(1, self.lenElements(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div") + 1):
                self.english_titles.append(self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/p[1]").get_attribute("textContent"))
                self.ratings.append(self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[4]/span").get_attribute("textContent"))
                self.runtimes.append(self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[2]/span").get_attribute("textContent").strip())

                hebrew_title = self.element(f"/html/body/div[4]/div[3]/div[2]/div[1]/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/h4").get_attribute("textContent")
                self.hebrew_titles.append(hebrew_title)

        self.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")

        self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dt/a", 0.2)
        for cinema in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li") + 1):
            self.screening_city = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a/span").get_attribute("textContent")
            self.screening_type = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a/span").get_attribute("textContent")

            self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a", 0.2)
            self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dt/a", 0.2)
            for day in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li") + 1):
                self.date_of_showing = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a").get_attribute("textContent")
                self.date_of_showing = datetime.strptime(re.search(r"\d{1,2}/\d{1,2}/\d{4}", self.date_of_showing).group(), "%d/%m/%Y").date().isoformat()

                self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a", 0.2)
                self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dt/a", 0.2)
                name_to_idx = {str(name): i for i, name in enumerate(self.hebrew_titles)}
                for film_index in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li") + 1):
                    checking_film_name = str(self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{film_index}]/a").get_attribute("textContent"))
                    checking_film = name_to_idx.get(checking_film_name)
                    if checking_film is None:
                        continue

                    self.rating = str(self.ratings[checking_film]).strip()
                    self.runtime = int(self.runtimes[checking_film])

                    self.english_title = str(self.english_titles[checking_film]).strip()
                    self.hebrew_title = str(self.hebrew_titles[checking_film]).strip()
                    if self.english_title == "" or self.english_title == None:
                        self.english_title = self.hebrew_title

                    if "מדובב לרוסית" in self.hebrew_title:
                        self.dub_language = "Russian"
                        self.hebrew_title = re.sub(r"\s*[-–—־]?\s*מדובב לרוסית\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                    elif "מדובב לצרפתית" in self.hebrew_title:
                        self.dub_language = "French"
                        self.hebrew_title = re.sub(r"\s*[-–—־]?\s*מדובב לצרפתית\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                    elif "בתרגום לצרפתית" in self.hebrew_title:
                        self.dub_language = "French"
                        self.hebrew_title = re.sub(r"\s*[-–—־]?\s*בתרגום לצרפתית\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                    elif "מדובב" in self.hebrew_title:
                        self.dub_language = "Hebrew"
                        self.hebrew_title = re.sub(r"\s*[-–—־]?\s*מדובב\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                    elif "אנגלית" in self.hebrew_title:
                        self.hebrew_title = re.sub(r"\s*[-–—־]?\s*אנגלית\s*[-–—־]?\s*", "", self.hebrew_title).strip()
                    else:
                        self.dub_language = None

                    self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{film_index}]/a", 0.2)
                    self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dt/a", 0.2)
                    for time in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li") + 1):
                        self.showtime = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a").get_attribute("textContent")

                        self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a", 0.2)

                        event_id = self.driver.execute_script(
                            """
                            return (function(node){
                                if (!window.ko) return null;
                                var data = ko.dataFor(node) || {};
                                var h2 = (data.selected && typeof data.selected.hour2 === "function" && data.selected.hour2())
                                        || (data.selected && typeof data.selected.hour === "function" && data.selected.hour());
                                return h2 && (h2.EventId || h2.EventID || h2.EventID1) || null;
                            })(arguments[0]);
                            """,
                            self.element("/html/body/div[4]/div[2]/div/div/div[2]/div/div[6]/button"),
                        )
                        self.english_href = f"https://tickets.cinema-city.co.il/order/{event_id}?lang=en"
                        self.hebrew_href = f"https://tickets.cinema-city.co.il/order/{event_id}?lang=he"

                        self.appendToGatheringInfo()
