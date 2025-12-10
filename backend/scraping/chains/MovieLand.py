from backend.scraping.BaseCinema import BaseCinema

from datetime import datetime
import re


class MovieLand(BaseCinema):
    CINEMA_NAME = "MovieLand"
    URL = "https://movieland.co.il/movies"
    HEADLESS = False

    def logic(self):
        self.sleep(5)
        self.tryExceptPass(lambda: self.waitAndClick("#sbuzz-confirm", 2))
        self.tryExceptPass(lambda: self.waitAndClick("#gdpr-module-message > div > div > div.gdpr-content-part.gdpr-accept > a", 2))
        self.click("#branch-1293", 1)

        for film_card in range(1, self.lenElements(f"/html/body/div[1]/div[10]/div[2]/div/div/div") + 1):
            self.hebrew_hrefs.append(self.element(f"/html/body/div[1]/div[10]/div[2]/div/div/div[{film_card}]/div/div/div/div[1]/a[1]").get_attribute("href"))

        for href in range(len(self.hebrew_hrefs)):
            self.driver.get(self.hebrew_hrefs[href])
            hebrew_name = self.element("#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(1)").text.strip()
            self.hebrew_titles.append(hebrew_name)
            self.english_titles.append(self.element("#change-bg > div > div:nth-child(3) > div > div.col-12.col-sm-8.col-md-8.col-lg-9 > div > div > div.bg-more-b > span:nth-child(3)").text.strip() or hebrew_name)
            self.original_languages.append(str(self.element(f"/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[16]").text.split(":", 1)[-1].strip()))
            release_year = self.element(f"/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[15]").text
            if re.search(r"\b\d{4}\b", release_year):
                self.release_years.append(int(re.search(r"\b\d{4}\b", release_year).group(0)))
            else:
                self.release_years.append(None)
            self.ratings.append(str(self.element(f"/html/body/div[1]/div[10]/div/div[3]/div/div[2]/div/div/div[2]/span[10]").text))
        name_to_idx = {str(name): i for i, name in enumerate(self.hebrew_titles)}

        # for cinema in range(1, self.lenElements("/html/body/div[1]/div[7]/ul/li[2]/div/div[1]/a") + 1):
        for cinema in range(1, 2):
            self.driver.get(self.element(f"body > div.rtl-wrapper > div.newnav-upper-menu.d-none.d-md-block > ul > li.dropdown > div > div:nth-child(1) > a:nth-child({cinema})").get_attribute("href").rsplit("/", 1)[0] + "/")
            self.sleep(1)
            self.zoomOut(30)

            self.screening_city = self.element("#change-bg > div.container-fluid.inner-page-header > div > h1").text

            self.click("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div", 0.5)
            found_first_day_of_next_month = False
            for checking_month in range(1, 3):
                if checking_month == 2:
                    self.click(f"#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.next", 0.5)

                checking_year = str(self.element("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div > div > div > div.datepicker-days > table > thead > tr:nth-child(2) > th.datepicker-switch").text.split()[-1])
                for week in range(1, self.lenElements(f"#events-list > div > div > div > div > div > div.datepicker-days > table > tbody > tr") + 1):
                    for day in range(1, 8):
                        self.click("#events-list > div.bd-days.br-v2.nav.nav-tabs.d-flex.d-md-block.justify-content-center > div > div", 0.2)
                        date_element = self.element(f"#events-list > div > div > div > div > div > div.datepicker-days > table > tbody > tr:nth-child({week}) > td:nth-child({day})")
                        day_test_num = date_element.text
                        if day_test_num != "1" and found_first_day_of_next_month == False and checking_month == 2:
                            continue
                        if day_test_num == "1" and found_first_day_of_next_month == False and checking_month == 2:
                            found_first_day_of_next_month = True
                        date_class_name = date_element.get_attribute("class")
                        if date_class_name == "day":
                            date_element.click()
                            self.sleep(1)

                            for film_index in range(1, self.lenElements("#events-list > div.bg-choose > div > div > div.col-12 > a") + 1):
                                elems = self.elements("#events-list > div.bg-choose > div")
                                if not elems or "לא נמצאו הקרנות" in elems[0].text:
                                    break

                                film_name = self.element(f"#events-list > div.bg-choose > div:nth-child({film_index}) > div > div.col-12 > a").text
                                checking_film = name_to_idx.get(film_name)
                                if checking_film is None:
                                    continue

                                self.english_title = self.english_titles[checking_film]
                                self.hebrew_title = self.hebrew_titles[checking_film]
                                self.release_year = self.release_years[checking_film]
                                self.rating = self.ratings[checking_film]

                                self.original_language = self.original_languages[checking_film]
                                if "(מדובב)" in self.hebrew_title:
                                    self.hebrew_title = self.hebrew_title.replace("(מדובב)", "").strip()
                                    self.dub_language = "Hebrew"

                                full_text = self.element(f"#events-list > div.bg-choose > div:nth-child({film_index}) > div > div.col-7.col-md-8.col-lg-9.col-xl-10.px-0.right-help > div.bg-day-c").text.strip()
                                date_part = full_text.split()[-1].replace(".", "/", 1) + f"/{checking_year}"
                                self.date_of_showing = datetime.strptime(date_part, "%d/%m/%Y").date().isoformat()

                                for screening_time in range(1, self.lenElements(f"/html/body/div[1]/div[10]/div[2]/div[1]/div/div/div/div[2]/div[4]/div[{film_index}]/div/div[3]/div[2]/div/div[2]/a") + 1):
                                    self.showtime = self.element(f"/html/body/div[1]/div[10]/div[2]/div[1]/div/div/div/div[2]/div[4]/div[{film_index}]/div/div[3]/div[2]/div/div[2]/a[{screening_time}]/div/span").text
                                    self.screening_type = "Upgrade" if self.lenElements(f"/html/body/div[1]/div[10]/div[2]/div[1]/div/div/div/div[2]/div[4]/div[{film_index}]/div/div[3]/div[2]/div/div[2]/a[{screening_time}]/div/img") else "Regular"
                                    self.english_href = self.element(f"/html/body/div[1]/div[10]/div[2]/div[1]/div/div/div/div[2]/div[4]/div[{film_index}]/div/div[3]/div[2]/div/div[2]/a[{screening_time}]").get_attribute("href")
                                    self.hebrew_href = self.element(f"/html/body/div[1]/div[10]/div[2]/div[1]/div/div/div/div[2]/div[4]/div[{film_index}]/div/div[3]/div[2]/div/div[2]/a[{screening_time}]").get_attribute("href")

                                    self.appendToGatheringInfo()
