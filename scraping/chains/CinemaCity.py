from scraping.chains.BaseCinema import BaseCinema
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json, re, time


def pfx(label, obj):
    try:
        print(f"[{label}] {json.dumps(obj, ensure_ascii=False, indent=2)[:2000]}")
    except Exception as e:
        print(f"[{label}] <non-serializable> {e}")


class CinemaCity(BaseCinema):
    CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/"

    def logic(self):
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('body > flashy-popup');if(el){el.remove();}")
        self.sleep(3)
        self.driver.execute_script("var el=document.querySelector('#popupVSChat');if(el){el.remove();}")
        self.sleep(3)
        self.zoomOut(50)
        self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dt/a")
        for cinema in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li") + 1):
            cinema_name = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a/span").text
            self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/dl/dd/ul/li[{cinema}]/a")
            self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dt/a")
            for day in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li") + 1):
                day_name = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a/span").text
                self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[3]/dl/dd/ul/li[{day}]/a")
                self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dt/a")
                for title in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li") + 1):
                    title_name = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{title}]/a/span").text
                    self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[4]/dl/dd/ul/li/div/div[1]/ul/li[{title}]/a")
                    self.jsClick("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dt/a")
                    for time in range(1, self.lenElements("/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li") + 1):
                        time_name = self.element(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a/span").text
                        self.jsClick(f"/html/body/div[4]/div[2]/div/div/div[2]/div/div[5]/dl/dd/ul/li[{time}]/a")

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

                        print(f"{cinema_name} - {day_name} - {title_name} - {time_name} - {event_id}")
