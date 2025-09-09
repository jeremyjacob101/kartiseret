from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class HotCinema(BaseCinema):
    CINEMA_NAME = "Hot Cinema"
    URL = "https://hotcinema.co.il/ShowingNow"

    def logic(self):
        self.sleep(2)
        self.click("/html/body/div[7]/div/button", 1)
        self.click("/html/body/div[3]/div/div/div[1]/a", 1)

        for film_card in range(1, 13):
            # for film_card in range(1, self.lenElements("/html/body/div[2]/div[4]/div[2]/div/div/div[2]/div/div/a") + 1):
            self.trying_hrefs.append(self.element(f"/html/body/div[2]/div[4]/div[2]/div/div/div[2]/div[{film_card}]/div/a").get_attribute("href"))
        for href in self.trying_hrefs:
            self.driver.get(href)
            self.sleep(0.1)

            self.trying_names.append(self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/h2").text.strip())
            self.trying_hebrew_names.append(self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/h1").text.strip())
            self.release_years.append(self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]").text.split()[-1].strip())
            self.ratings.append(self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[2]/div[2]/span").text.strip())
            try:
                self.runtimes.append(int(re.sub(r"\D", "", self.element("/html/body/div[2]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/span").text.strip())))
            except:
                self.runtimes.append(None)
        name_to_idx = {str(name).lower(): i for i, name in enumerate(self.trying_hebrew_names)}

        for cinema in range(1, self.lenElements("/html/body/div[2]/div[1]/div/div/div[1]/div[3]/div[2]/div[2]/a") + 1):
            self.driver.get(self.element(f"/html/body/div[2]/div[1]/div/div/div[1]/div[3]/div[2]/div[2]/a[{cinema}]").get_attribute("href"))
            self.sleep(1.5)
            self.zoomOut(50)
            self.screening_city = self.element("/html/body/div[2]/div[4]/div[1]/div/div/div/div[2]/h1").text.strip()

            for checking_month in range(1, 3):
                for week in range(1, 7):
                    for day in range(1, 8):
                        self.driver.execute_script("$('.datepicker-wrapper input').datepicker('show')")
                        day_class_label = self.element(f"/html/body/div[6]/div[1]/table/tbody/tr[{week}]/td[{day}]").get_attribute("class").strip()
                        if day_class_label == "day disabled" or day_class_label == "old day" or day_class_label == "old day disabled":
                            continue
                        self.click(f"/html/body/div[6]/div[1]/table/tbody/tr[{week}]/td[{day}]", 0.25)
                        self.date_of_showing = self.element("/html/body/div[2]/div[4]/div[2]/div/div[3]/div/div/div/div[1]/div").get_attribute("innerHTML").strip().split("\n")[0].strip()

                        for film_index in range(1, self.lenElements("/html/body/div[2]/div[4]/div[2]/div/div[2]/div/div/div/div/table/tbody/tr") + 1):
                            checking_film_name = str(self.element(f"/html/body/div[2]/div[4]/div[2]/div/div[2]/div/div/div/div/table/tbody/tr[{film_index}]/td[1]").text)
                            checking_film = name_to_idx.get(checking_film_name)
                            if checking_film is None:
                                continue

                            self.english_title = str(self.trying_names[checking_film])
                            self.hebrew_title = str(self.trying_hebrew_names[checking_film])

                            if "מדובב לעברית" in self.hebrew_title:
                                self.dub_language = "Hebrew"
                                self.hebrew_title = self.hebrew_title.replace("מדובב לעברית", "").strip()
                            if "מדובב לרוסית" in self.hebrew_title:
                                self.dub_language = "Russian"
                                self.hebrew_title = self.hebrew_title.replace("מדובב לרוסית", "").strip()

                            row_xpath = f"/html/body/div[2]/div[4]/div[2]/div/div[2]/div/div/div/div/table/tbody/tr[{film_index}]"
                            row_el = self.element(row_xpath)

                            time_to_event = self.driver.execute_script(
                                r"""
                            return (function(row){
                            function norm(s){ return String(s||'').replace(/\s+/g,' ').trim(); }
                            function hhmm(s){ var m=String(s||'').match(/\b(?:[01]?\d|2[0-3]):[0-5]\d\b/); return m?m[0]:null; }

                            const title = norm(row?.querySelector('td:first-child')?.innerText);
                            if (!title) return {};

                            // find Vue instance (Vue 2 or 3)
                            let n = document.querySelector('#order-panel')
                                    || document.querySelector('div.table-responsive')
                                    || document.querySelector('table')
                                    || document.body;
                            while (n && !n.__vue__ && !n.__vueParentComponent) n = n.parentNode;
                            let vm = n ? (n.__vue__ || n.__vueParentComponent) : null;
                            vm = vm && (vm.ctx || vm);

                            const events = vm?.events || vm?._data?.events || [];
                            let movie = events.find(e => norm(e.MovieName) === title)
                                    || events.find(e => norm(e.MovieName).includes(title) || title.includes(norm(e.MovieName)));
                            if (!movie) return {};

                            const map = {};
                            (movie.Dates || []).forEach(d => {
                                const t = hhmm(d.Hour) || hhmm(d.FormattedDate) || hhmm(d.Date);
                                const id = d && (d.EventId ?? d.eventId ?? d.Id ?? d.id);
                                if (t && id != null) map[t] = String(id);
                            });
                            return map;
                            })(arguments[0]);
                            """,
                                row_el,
                            )

                            # for showtime in range(1, self.lenElements(f"/html/body/div[2]/div[4]/div[2]/div/div[2]/div/div/div/div/table/tbody/tr[{film_index}]/td[5]/a") + 1):
                            for showtime in range(1, self.lenElements(f"{row_xpath}/td[5]/a") + 1):
                                showtime_element = self.element(f"{row_xpath}/td[5]/a[{showtime}]")
                                full_showtime_text = str(showtime_element.get_attribute("innerHTML"))
                                self.screening_type = "Premium" if "PREMIUM" in full_showtime_text else "Regular"
                                self.showtime = re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", full_showtime_text).group(0)

                                event_id = time_to_event.get(self.showtime)
                                href_index = re.search(r"/theater/(\d+)", self.element(f"/html/body/div[2]/div[1]/div/div/div[1]/div[3]/div[2]/div[2]/a[{cinema}]").get_attribute("href"))
                                href_index = int(href_index.group(1)) if href_index else None

                                idToTix = {16: 1197, 14: 1194, 1: 1183, 17: 1191, 9: 1195, 2: 1184, 15: 1192, 6: 1181, 8: 1193, 5: 1182, 3: 1196, 22: 1198}

                                href_index = idToTix.get(href_index)

                                use_this_href = f"tickets.hotcinema.co.il/site/{href_index}/tickets?code={href_index}-{event_id}"
                                self.english_href = use_this_href + "&languageid=en_gb"
                                self.hebrew_href = use_this_href + "&languageid=he_IL"

                                self.release_year = self.release_years[checking_film]
                                self.rating = self.ratings[checking_film]

                                self.appendToGatheringInfo()
                                self.printShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
