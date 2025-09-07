from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class MovieLand(BaseCinema):
    CINEMA_NAME = "MovieLand"
    URL = "https://movieland.co.il/"

    def logic(self):
        print(f"\nMovieland\n")

        self.sleep(5)
        self.waitAndClick("#sbuzz-confirm", 2)
        self.waitAndClick("#chooseTheaterModalCenter > div > div > a", 2)

        num_movies = self.lenElements(f"#change-bg > div.container-fluid.pb-5.px-0.px-md-4 > div > div > div")
        for i in range(1, num_movies + 1):
            text_content = self.element(f"#change-bg > div.container-fluid.pb-5.px-0.px-md-4 > div > div > div:nth-child({i}) > div > div > div > div.front > a.d-block > div > div.o-name").text
            if "מדובב" in text_content:
                continue

            element = self.element(f"#change-bg > div.container-fluid.pb-5.px-0.px-md-4 > div > div > div:nth-child({i}) > div > div > div > div.front > a.d-block")
            href = element.get_attribute("href")
            self.trying_hrefs.append(href)

        for i in range(len(self.trying_hrefs)):
            self.driver.get(self.trying_hrefs[i])

            working_title = self.element(f"#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(3)").text
            hebrew_title = self.element(f"#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(1)").text

            print(working_title)

                self.items["hrefs"].append(trying_hrefs[i])
                self.items["runtimes"].append(actual_runtime)
                self.items["titles"].append(actual_title)
                self.items["hebrew_titles"].append(hebrew_title)
                self.items["popularity"].append(sself.ite_popularity)
                self.items["imdbIDs"].append(imdb_id)
                self.items["imdbScores"].append(imdb_rating)
                self.items["imdbVotes"].append(imdb_votes)
                self.items["rtScores"].append(rt_rating)

        for i in range(1, 5):
            self.sleep(0.4)
            theater_id = self.element(f"body > div.rtl-wrapper > div.newnav-upper-menu.d-none.d-md-block > ul > li.dropdown > div > div:nth-child(1) > a:nth-child({i})")
            relative_href = theater_id.get_attribute("href")
            final_url = relative_href.rsplit("/", 1)[0] + "/"

            self.driver.get(final_url)

            self.sleep(0.5)
            self.driver.execute_script("document.body.style.zoom='30%'")
            self.sleep(0.4)

            theater_name = self.element("#change-bg > div.container-fluid.inner-page-header > div > h1").text
            theater_replace = {
                "כרמיאל": "Carmiel",
                "חיפה": "Haifa",
                "נתניה": "Netanya",
                'הצוק ת"א': "Glilot",
            }
            theater_name = theater_replace.get(theater_name, theater_name)

            # open calendar:
            self.element("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div").click()
            self.sleep(0.5)
            found_first_day_of_next_month = False
            for x in range(0,2):
                if x == 1:
                    next_month_click = f"#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.next"
                    self.element(next_month_click).click()
                    # print(f"CLICKED ON NEXT MONTH")

                get_current_year = self.element("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.datepicker-switch").text
                use_this_year = get_current_year.split()[-1]

                for w in range(1, self.lenElements(f"#events-list > div > div > div > div > div > div.datepicker-days > table > tbody > tr") + 1):
                    for d in range(1, 8):
                        self.element("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div").click()
                        self.sleep(0.2)
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
                            num_films_on_this_day = self.element("#events-list > div.bg-choose > div > div > div.col-12 > a")
                            # print(f"num_films_on_this_day: {len(num_films_on_this_day)}")
                            # for film in num_films_on_this_day:
                            #     print(f"\t{film.text}")
                            for j in range(1, len(num_films_on_this_day) + 1):
                                try:
                                    check_if_empty_films_day = f"#events-list > div.bg-choose > div"
                                    check_if_empty_films_day_div = self.element(check_if_empty_films_day).text
                                    if "לא נמצאו הקרנות" in check_if_empty_films_day_div:
                                        break
                                except:
                                    break
                                movie_names_per_day = f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-12 > a"
                                movie_name = self.element(movie_names_per_day).text
                                for k in range(len(self.items["hebrew_titles"])):
                                    if movie_name == self.items["hebrew_titles"][k]:
                                        in_movie_date = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div.bg-day-c")
                                        full_text = in_movie_date.text.strip()
                                        date_part = full_text.split()[-1]
                                        date_part = str(date_part) + "/" + str(use_this_year)
                                        date_part = date_part.replace(".", "/", 1)
                                        # print(f"    {date_part}")

                                        # print(f"        {items['titles'][k]}")

                                        num_showtimes = self.lenElements(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a")
                                        # print(f"num_showtimes: {num_showtimes}")
                                        for l in range(1, num_showtimes + 1):
                                            time_text = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l}) > div > span").text
                                            type_text = "R"
                                            try:
                                                premium_try = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l}) > div > img")
                                                type_text = "Upgrade"
                                            except:
                                                pass
                                            # print(f"            {time_text} -- {type_text}")

                                            time_href = self.element(f"#events-list > div.bg-choose > div:nth-child({j}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div:nth-child(2) > div > div.bg-hours2.bg-hours2-a > a:nth-child({l})").get_attribute("href")
                                            time_href = time_href.split('eventID=')[1].split('&')[0]

        # In each showtime -
        # self.appendToGatheringInfo()
        # self.printShowtime()

        # At end -
        # turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        # self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
