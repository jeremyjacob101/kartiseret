from scraping.comingsoons.BaseSoon import BaseSoon

from datetime import datetime
import re


class CCsoon(BaseSoon):
    SOON_CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/comingsoon"

    def logic(self):
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('body > flashy-popup');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#popupVSChat');if(el){el.remove();}")
        self.sleep(5)
        self.zoomOut(50)

        for _ in range(10):
            element = self.element("#change-bg > div > div > div > div.movies.row > div > p > a")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.sleep(1)
            try:
                element.click()
                self.sleep(3)
            except:
                break

        for cinema_block in range(1, self.lenElements("#moviesContainer > div", "row mainThumbWrapper") + 1):
            for film_card in range(1, self.lenElements(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div") + 1):
                self.hebrew_title = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[1]/div/h2").get_attribute("textContent").strip()
                self.english_title = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/p[1]").get_attribute("textContent").strip()
                self.runtime = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[2]/span").get_attribute("textContent").strip()
                self.rating = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/div[1]/p[4]/span").get_attribute("textContent").strip()
                self.helper_href = self.element(f"/html/body/div[4]/div/div/div/div[1]/div[2]/div/div[{cinema_block}]/div[{film_card}]/div/div/div[2]/div/ul/li[1]/a").get_attribute("href")

                self.appendToGatheringInfo()
                self.printComingSoon()

        turn_info_into_dictionaries = [dict(zip(self.gathering_info.keys(), values)) for values in zip(*self.gathering_info.values())]
        self.supabase.table("testingSoons").insert(turn_info_into_dictionaries).execute()
