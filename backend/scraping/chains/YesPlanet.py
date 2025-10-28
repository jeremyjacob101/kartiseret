from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class YesPlanet(BaseCinema):
    CINEMA_NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_gb#/"

    def logic(self):
        self.sleep(10)
        self.waitAndClick("#onetrust-accept-btn-handler", 1)

        self.click("#header-select-location")
        self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
        self.click(f"/html/body/div[12]/div[2]/div/ul/li[1]/a")
        self.driver.get(self.URL)
        self.sleep(3)

        for film_card in range(1, self.lenElements("/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div")):
            self.english_hrefs.append(str(self.element(f"/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a").get_attribute("href")))
            self.english_titles.append(str(self.element(f"/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div[{film_card}]/a/p").text))
        for href in self.english_hrefs:
            self.driver.get(href)
            self.sleep(0.1)

            self.hebrew_titles.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(1) > dd").text))
            release_year = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text
            if re.search(r"\b\d{4}\b", release_year):
                self.release_years.append(int(re.search(r"\b\d{4}\b", release_year).group(0)))
            else:
                self.release_years.append(None)

            self.directed_bys.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(4) > dd").text))

            original_language = str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(6) > dd").text)
            if "HEB" in original_language or original_language == "":
                original_language = "HEB"
            self.original_languages.append(original_language)

            rating = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(7) > dd").text
            if rating:
                self.ratings.append(str(rating))

            runtime = self.element("/html/body/div[5]/section[2]/div/div[2]/div[1]/div[1]/div[2]/p").text.strip()
            if runtime and (m := re.search(r"\d+", runtime)):
                self.runtimes.append(int(m.group()))
        name_to_idx = {str(name).lower(): i for i, name in enumerate(self.english_titles)}

        for cinema in range(1, 7):
            if cinema == 1:
                self.click("/html/body/div[3]/div/div[1]/div[1]/div/div[2]/nav/div/ul/li[1]/div/a[1]")
            else:
                self.click("#header-change-location")
                self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
                self.click(f"body > div.selectpicker-dropdown-container.npm-quickbook > div.bs-container.btn-group.bootstrap-select.qb-.open > div > ul > li:nth-child({cinema}) > a")
            self.zoomOut(30)
            self.sleep(1)

            self.screening_city = self.element("/html/body/section[3]/section/div[1]/div/div/div[1]/div/h2").text

            found_first_day_of_next_month = False
            for checking_month in range(1, 3):
                if found_first_day_of_next_month == False and checking_month == 2:
                    continue

                self.click("/html/body/section[3]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]", 0.5)
                for week in range(1, self.lenElements("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr") + 1):
                    for day in range(1, 8):
                        if found_first_day_of_next_month == True and checking_month == 1:
                            continue

                        self.click("/html/body/section[3]/section/div[1]/div/div/div[2]/div[1]/div/div[1]/button[8]", 0.5)

                        if checking_month == 2:
                            self.click("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > thead > tr:nth-child(1) > th.next", 0.25)

                        day_number = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({week}) > td:nth-child({day})").get_attribute("class")
                        if day_number == "disabled highlighted day disabled" or day_number == "old disabled highlighted day disabled" or day_number == "old day active selected" or day_number == "old day active" or day_number == "old day disabled" or day_number == "day disabled" or (day_number == "new day disabled" and checking_month == 2):
                            continue
                        if (day_number == "new day active" or day_number == "new day disabled") and (found_first_day_of_next_month == False) and (checking_month == 1):
                            found_first_day_of_next_month = True
                            continue

                        self.click(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({week}) > td:nth-child({day}) > button", 0.5)
                        date_name = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.col-xs-12.mb-sm > h5").text
                        self.date_of_showing = datetime.strptime(date_name.split(" ", 1)[1], "%d/%m/%Y").date().isoformat()

                        self.sleep(3)
                        for film_index in range(1, self.lenElements("/html/body/section[3]/section/div[1]/div/section/div[2]/div") + 1):
                            selector = f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/h4"
                            if self.lenElements(selector) and self.element(selector).text == "PRE-ORDER YOUR TICKETS NOW":
                                continue

                            checking_film_name = str(self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[1]/a/h3").text).lower()
                            checking_film = name_to_idx.get(checking_film_name)
                            if checking_film is None:
                                continue

                            is_it_dubbed_1 = self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/ul[2]/li[2]/span") > 0 and self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div/div/ul[2]/li[2]/span").text == "DUB"
                            is_it_dubbed_2 = self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[2]/div/ul[2]/li[4]/span") > 0 and self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[2]/div/ul[2]/li[4]/span").text == "DUB"
                            self.dub_language = "Hebrew" if is_it_dubbed_1 or is_it_dubbed_2 else None

                            for showtype in range(1, self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div") + 1):
                                self.screening_type = str(self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/ul[1]/li/span").text)
                                if self.screening_type == "2D":
                                    self.screening_type = "Regular"

                                for showtime in range(1, self.lenElements(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/a") + 1):
                                    self.showtime = self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/a[{showtime}]").text
                                    self.english_href = self.element(f"/html/body/section[3]/section/div[1]/div/section/div[2]/div[{film_index}]/div/div/div[2]/div/div[2]/div[{showtype}]/div/a[{showtime}]").get_attribute("data-url").replace("/api", "")
                                    self.hebrew_href = self.english_href.replace("lang=en", "lang=he")

                                    self.original_language = self.original_languages[checking_film]
                                    self.release_year = self.release_years[checking_film]
                                    self.directed_by = self.directed_bys[checking_film]
                                    self.rating = self.ratings[checking_film]
                                    self.runtime = self.runtimes[checking_film]

                                    self.english_title = self.english_titles[checking_film]
                                    self.hebrew_title = self.hebrew_titles[checking_film]

                                    self.appendToGatheringInfo()
