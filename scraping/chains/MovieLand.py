from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class MovieLand(BaseCinema):
    CINEMA_NAME = "MovieLand"
    URL = "https://movieland.co.il/"

    def logic(self):
        self.sleep(5)
        self.waitAndClick("#sbuzz-confirm", 2)
        self.waitAndClick("#gdpr-module-message > div > div > div.gdpr-content-part.gdpr-accept > a", 2)
        self.click("#branch-1293", 1)

        for i in range(1, self.lenElements(f"#change-bg > div.container-fluid.pb-5.px-0.px-md-4 > div > div > div") + 1):
            self.trying_hrefs.append(self.element(f"#change-bg > div.container-fluid.pb-5.px-0.px-md-4 > div > div > div:nth-child({i}) > div > div > div > div.front > a.d-block").get_attribute("href"))

        for i in range(len(self.trying_hrefs)):
            self.driver.get(self.trying_hrefs[i])
            self.trying_names.append(self.element(f"#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(3)").text)
            self.trying_hebrew_names.append(self.element(f"#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(1)").text)

        for i in range(1, 7):
            self.driver.get(self.element(f"body > div.rtl-wrapper > div.newnav-upper-menu.d-none.d-md-block > ul > li.dropdown > div > div:nth-child(1) > a:nth-child({i})").get_attribute("href").rsplit("/", 1)[0] + "/")

            self.sleep(0.5)
            self.zoomOut(30)
            self.sleep(0.5)

            self.screening_city = self.element("#change-bg > div.container-fluid.inner-page-header > div > h1").text

            self.click("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div", 0.5)
            found_first_day_of_next_month = False
            for x in range(0,2):
                if x == 1:
                    self.click(f"#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.next", 0.5)

                get_current_year = self.element("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.datepicker-switch").text
                print(f"\n\n\n\n{get_current_year}\n\n\n\n")
                y = get_current_year.split()[-1]

                for w in range(1, self.lenElements(f"#events-list > div > div > div > div > div > div.datepicker-days > table > tbody > tr") + 1):
                    for d in range(1, 8):
                        self.click("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div", 0.2)
                        date_element = self.element(f"#events-list > div > div > div > div > div > div.datepicker-days > table > tbody > tr:nth-child({w}) > td:nth-child({d})")
                        day_test_num = date_element.text
                        if day_test_num != "1" and found_first_day_of_next_month == False and x == 1:
                            continue
                        if day_test_num == "1" and found_first_day_of_next_month == False and x == 1:
                            found_first_day_of_next_month = True
                        date_class_name = date_element.get_attribute("class")
                        if date_class_name == "day":
                            date_element.click()
                            self.sleep(0.3)

                            for j in range(1, self.lenElements("#events-list > div.bg-choose > div > div > div.col-12 > a") + 1):
                                try:
                                    check_if_empty_films_day_div = self.element(f"#events-list > div.bg-choose > div").text
                                    if "לא נמצאו הקרנות" in check_if_empty_films_day_div:
                                        break
                                except:
                                    break
                                movie_names_per_day = f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-12 > a"
                                movie_name = self.element(movie_names_per_day).text
                                for k in range(len(self.trying_hebrew_names)):
                                    if movie_name == self.trying_hebrew_names[k]:
                                        self.english_title = self.trying_names[k]
                                        self.hebrew_title = self.trying_hebrew_names[k]

                                        in_movie_date = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div.bg-day-c")
                                        full_text = in_movie_date.text.strip()
                                        date_part = full_text.split()[-1]
                                        date_part = str(date_part) + "/" + str(y)
                                        date_part = date_part.replace(".", "/", 1)
                                        self.date_of_showing = datetime.strptime(date_part, "%d/%m/%Y").date().isoformat()

                                        for l in range(1, self.lenElements(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a") + 1):
                                            self.showtime = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l}) > div > span").text
                                            self.screening_type = "Regular"
                                            try:
                                                premium_try = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l}) > div > img")
                                                self.screening_type = "Upgrade"
                                            except:
                                                pass

                                            self.english_href = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l})").get_attribute("href")
                                            self.hebrew_href = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l})").get_attribute("href")

                                            self.appendToGatheringInfo()
                                            self.printShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
