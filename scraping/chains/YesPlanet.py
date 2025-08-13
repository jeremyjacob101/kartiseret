from scraping.chains.BaseCinema import BaseCinema

import re


class YesPlanet(BaseCinema):
    NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_GB#/"

    def logic(self):
        print(f"scraping yes planet")
        self.sleep(5)
        self.waitAndClick("#onetrust-accept-btn-handler")

        self.click("#header-select-location")
        self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
        self.click(f"/html/body/div[12]/div[2]/div/ul/li[1]/a")
        self.driver.get(self.URL)
        self.sleep(2)

        # Step 2: navigate to each href
        for i, href in enumerate([el.get_attribute("href") for el in self.elements("/html/body/div[6]/section/div[2]/div/div/div/div[2]/div/div/div/div[1]/div/a") if el.get_attribute("href")], start=1):
            print(f"trying to get href #{i}: {href}")
            self.driver.get(href)
            print(f"travelled to href #{i}")

            self.trying_names.append(str(self.element("/html/body/div[5]/section[1]/div/div[1]/div/p/span").text))
            self.trying_hebrew_names.append(str(self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(1) > dd").text))
            self.release_years.append(int(re.search(r"\b\d{4}\b", self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(5) > dd").text.strip()).group(0)))
            audio = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(6) > dd").text
            if ("HE" in audio):
                audio = "HE"
            language_dictionary = {"EN": "English", "FR": "French", "HE": "Hebrew"}
            self.audio_languages.append(str(language_dictionary.get(audio, audio)))
            rating = self.element("#more-info > div > div:nth-child(2) > div.col-md-8.col-sm-6.col-xs-12 > dl > div:nth-child(7) > dd").text
            if rating == "No limit":
                rating = "All Ages"
            if rating == "Other":
                rating = "14+"
            self.ratings.append(str(rating))

        for i in range(1, 7):
            self.click("#header-change-location")
            self.click("body > div.modal.location-picker-modal.fade.search.in > div > div > div > div:nth-child(2) > div:nth-child(3) > div.row.all-cinemas-list > div > div > div > button")
            self.click(f"/html/body/div[12]/div[2]/div/ul/li[{i}]/a")
            self.zoomOut(30)

            found_first_day_of_next_month = False
            for x in range(1, 3):
                if found_first_day_of_next_month == False and x == 2:
                    continue

                self.click("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > button.btn.btn-primary.datepicker-toggle")
                for w in range(1, self.lenElements("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr") + 1):
                    for d in range(1, 8):
                        if found_first_day_of_next_month == True and x == 1:
                            continue

                        self.click("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > button.btn.btn-primary.datepicker-toggle")

                        if x == 2:
                            self.click("body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > thead > tr:nth-child(1) > th.next")

                        day_number = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({w}) > td:nth-child({d})").get_attribute("class")

                        if day_number == "disabled highlighted day disabled" or day_number == "old disabled highlighted day disabled" or day_number == "old day active selected" or day_number == "old day active" or day_number == "old day disabled" or day_number == "day disabled" or (day_number == "new day disabled" and x == 2):
                            continue

                        if (day_number == "new day active" or day_number == "new day disabled") and (found_first_day_of_next_month == False) and (x == 1):
                            found_first_day_of_next_month = True
                            continue

                        self.click(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.qb-days-group.btn-group > div > div:nth-child(3) > div > div.datepicker.datepicker-inline > div.datepicker-days > table > tbody > tr:nth-child({w}) > td:nth-child({d}) > button")
                        date_name = self.element(f"body > section.light.quickbook-section.npm-quickbook > section > div:nth-child(1) > div > div > div:nth-child(2) > div.col-xs-12.col-md-6.qb-calendar-widget > div > div.col-xs-12.mb-sm > h5").text
                        date_name = date_name.split(" ", 1)[1]

                        print(f"\t{date_name}")
                        for i in range(1, self.lenElements("/html/body/section[3]/section/div[1]/div/section/div[2]/div") + 1):
                            print("implement per day logic")
                            self.sleep()
