from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class YesPlanet(BaseCinema):
    CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    def logic(self):
        self.sleep(5)
        self.waitAndClick("#onetrust-accept-btn-handler")

        self.click("#header-select-location")
        self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
        self.click(f"/html/body/div[12]/div[2]/div/ul/li[1]/a")
        self.driver.get(self.URL)
        self.sleep(2)

        for i in range(1, self.lenElements("/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div")):
            self.trying_names.append(str(self.element(f"/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div[{i}]/a/p").text))
            self.trying_hrefs.append(str(self.element(f"/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div[{i}]/a").get_attribute("href")))
        for href in self.trying_hrefs:
            self.driver.get(href)

            self.trying_hebrew_names.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(1) > dd").text))
            self.release_years.append(int(re.search(r"\b\d{4}\b", self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text.strip()).group(0)))
            self.directed_bys.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(4) > dd").text))

            self.original_language = str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(6) > dd").text)
            if "HE" in self.original_language:
                self.original_language = "HE"
            if self.original_language == "":
                self.original_language = None
            language_dictionary = {"EN": "English", "FR": "French", "HE": "Hebrew"}
            self.original_languages.append(str(language_dictionary.get(self.original_language, self.original_language)))

            rating = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(7) > dd").text
            if rating == "No limit":
                rating = "All"
            if rating == "Other":
                rating = "14+"
            self.ratings.append(str(rating))

        for cinema in range(1, 7):
            if cinema == 1:
                self.click("/html/body/div[3]/div/div[1]/div[1]/div/div[2]/nav/div/ul/li[1]/div/a[1]")
            else:
                self.click("#header-change-location")
                self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
                self.click(f"body > div.selectpicker-dropdown-container.npm-quickbook > div.bs-container.btn-group.bootstrap-select.qb-.open > div > ul > li:nth-child({cinema}) > a")
            self.zoomOut(30)

            self.screening_city = self.element("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(1) > div > h2").text
            self.fixCinemaNames()

            found_first_day_of_next_month = False
            for calendar_month in range(1, 3):
                if found_first_day_of_next_month == False and calendar_month == 2:
                    continue

                self.click("/html/body/section[3]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]")
                for w in range(1, self.lenElements("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr") + 1):
                    for d in range(1, 8):
                        if found_first_day_of_next_month == True and calendar_month == 1:
                            continue

                        self.click("/html/body/section[3]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]")

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

                        self.sleep(0.3)
                        for film_index in range(1, self.lenElements("/html/body/section[3]/section/div[1]/div/section/div[2]/div") + 1):
                            try:
                                skip_pre_order = self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/h4").text
                                if skip_pre_order == "PRE-ORDER YOUR TICKETS NOW":
                                    continue
                            except:
                                pass
                            try:
                                checking_film_name = str(self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[1]/a/h3").text).lower()
                            except:
                                continue
                            for checking_film in range(len(self.trying_names)):
                                if checking_film_name == str(self.trying_names[checking_film]).lower():
                                    try:
                                        self.dubbed_or_not = self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[2]/div/ul[2]/li[4]/span").text == "DUB"
                                    except:
                                        self.dubbed_or_not = False
                                    for showtype in range(1, self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div") + 1):
                                        self.screening_type = str(self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/ul[1]/li/span").text)
                                        if self.screening_type == "2D":
                                            self.screening_type = "Regular"
                                        for showtime in range(1, self.lenElements(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a")):
                                            self.showtime = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a:nth-child({showtime + 1})").text
                                            self.english_href = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > section > div.container > div:nth-child({film_index}) > div > div > div:nth-child(2) > div > div.events.col-xs-12 > div:nth-child({showtype}) > div > a:nth-child({showtime + 1})").get_attribute("data-url").replace("/api", "")
                                            self.hebrew_href = self.english_href.replace("lang=en", "lang=he")

                                            self.showtime_id = str(self.getRandomHash())
                                            self.scraped_at = str(self.getJlemTimeNow())

                                            self.release_year = self.release_years[checking_film]
                                            self.original_language = self.original_languages[checking_film]
                                            self.rating = self.ratings[checking_film]

                                            self.english_title = self.trying_names[checking_film]
                                            self.hebrew_title = self.trying_hebrew_names[checking_film]

                                            self.appendToGatheringInfo()

                                            print(f"{self.showtime_id:9} - {self.english_title:24} - {self.CINEMA_NAME:12} - {(self.release_year if self.release_year is not None else '----'):4} - {self.original_language:10} - {self.english_href:.26} - {self.screening_city:15} - {self.date_of_showing:10} - {self.showtime:5} - {self.screening_type:.10}")

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingMovies").insert(turn_info_into_dictionaries).execute()
