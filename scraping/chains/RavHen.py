from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class RavHen(BaseCinema):
    CINEMA_NAME = "Rav Hen"
    URL = "https://www.rav-hen.co.il/#/"

    def logic(self):
        self.sleep(5)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        self.click("#header-select-location")
        self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
        self.click(f"/html/body/div[12]/div[2]/div/ul/li[1]/a")
        self.driver.get(self.URL)
        self.sleep(2)

        for film_card in range(1, self.lenElements("/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div") + 1):
            self.trying_hrefs.append(str(self.element(f"/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a").get_attribute("href")))

        for href in self.trying_hrefs:
            self.driver.get(href)
            self.trying_names.append(str(self.element("/html/body/div[5]/section[1]/div/div[2]/div[1]/div/ul/li/h1").text))
            self.trying_hebrew_names.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(1) > dd").text))
            trying_year = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text
            if re.search(r"\b\d{4}\b", trying_year):
                self.release_years.append(int(re.search(r"\b\d{4}\b", trying_year).group(0)))
            else:
                self.release_years.append(None)
            self.original_languages.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(6) > dd").text))
            self.ratings.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(7) > dd").text))
        name_to_idx = {str(name): i for i, name in enumerate(self.trying_hebrew_names)}

        for cinema in range(1, 4):
            if cinema == 1:
                self.click("/html/body/div[3]/div/div[1]/div[1]/div/div[2]/nav/div/ul/li[1]/div/a[1]")
            else:
                self.click("#header-change-location")
                self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
                self.click(f"body > div.selectpicker-dropdown-container.npm-quickbook > div.bs-container.btn-group.bootstrap-select.qb-.open > div > ul > li:nth-child({cinema}) > a")
            self.zoomOut(30)
            self.sleep(1)

            self.screening_city = self.element("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(1) > div > h2").text

            found_first_day_of_next_month = False
            for calendar_month in range(1, 3):
                if found_first_day_of_next_month == False and calendar_month == 2:
                    continue

                self.click("/html/body/section[2]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]")
                for w in range(1, self.lenElements("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr") + 1):
                    for d in range(1, 8):
                        if found_first_day_of_next_month == True and calendar_month == 1:
                            continue

                        self.click("/html/body/section[2]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]")

                        if calendar_month == 2:
                            self.click("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > thead > tr:nth-child(1) > th.next")

                        day_number = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({w}) > td:nth-child({d})").get_attribute("class")
                        if day_number == "disabled highlighted day disabled" or day_number == "old disabled highlighted day disabled" or day_number == "old day active selected" or day_number == "old day active" or day_number == "old day disabled" or day_number == "day disabled" or (day_number == "new day disabled" and calendar_month == 2):
                            continue
                        if (day_number == "new day active" or day_number == "new day disabled") and (found_first_day_of_next_month == False) and (calendar_month == 1):
                            found_first_day_of_next_month = True
                            continue

                        self.click(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({w}) > td:nth-child({d}) > button")
                        date_name = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.col-xs-12.mb-sm > h5").text
                        self.date_of_showing = datetime.strptime(date_name.split(" ", 1)[1], "%d/%m/%Y").date().isoformat()
                        self.sleep(0.5)

                        # Find all film elements first
                        film_elements = self.elements("/html/body/section[2]/section/div[1]/div/section/div[2]/div")

                        # Print total count
                        print(f"Found {len(film_elements)} films:")

                        # Print them in a numbered list
                        for film_index, el in enumerate(film_elements, start=1):
                            try:
                                title = self.element(f"/html/body/section[2]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[1]/a/h3").text
                            except Exception:
                                title = "<missing title>"
                            print(f"{film_index}. {title}")

                        for film_index in range(1, self.lenElements("/html/body/section[2]/section/div[1]/div/section/div[2]/div") + 1):
                            checking_film_name = str(self.element(f"/html/body/section[2]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[1]/a/h3").text).lower()
                            checking_film = name_to_idx.get(checking_film_name)
                            if checking_film is None:
                                continue

                            is_it_dubbed_1 = self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/ul[2]/li[2]/span") > 0 and self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/ul[2]/li[2]/span").text == "מדובב"
                            is_it_dubbed_2 = self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[2]/div/ul[2]/li[4]/span") > 0 and self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[2]/div/ul[2]/li[4]/span").text == "מדובב"
                            self.dub_language = "Hebrew" if is_it_dubbed_1 or is_it_dubbed_2 else None

                            for showtype in range(1, self.lenElements(f"/html/body/section[2]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div") + 1):
                                self.screening_type = str(self.element(f"/html/body/section[2]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/ul[1]/li/span").text)
                                if self.screening_type == "2D":
                                    self.screening_type = "Regular"

                                for showtime in range(1, self.lenElements(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a") + 1):
                                    self.showtime = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a:nth-child({showtime + 1})").text
                                    self.sleep(0.1)
                                    self.english_href = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a:nth-child({showtime + 1})").get_attribute("data-url").replace("/api", "")
                                    self.hebrew_href = self.english_href.replace("lang=en", "lang=he")

                                    self.original_language = self.original_languages[checking_film]
                                    self.release_year = self.release_years[checking_film]
                                    self.rating = self.ratings[checking_film]

                                    self.english_title = self.trying_names[checking_film]
                                    self.hebrew_title = self.trying_hebrew_names[checking_film]

                                    self.appendToGatheringInfo()
                                    # self.printShowtime()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
