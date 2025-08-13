from scraping.chains.BaseCinema import BaseCinema


class YesPlanet(BaseCinema):
    NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_GB#/"

    def logic(self):
        print(f"scraping yes planet")
        self.sleep(5)
        self.waitAndClick("#onetrust-accept-btn-handler")
        self.zoomOut(50)

        for i in range(1, self.lenElements("/html/body/div[12]/div[2]/div/ul/li")):
            print("d")
            self.click("#header-select-location" if i == 1 else "#header-change-location")
            self.click("/html/body/div[16]/div/div/div/div[2]/div[3]/div[2]/div/div/div/button")
            self.click(f"/html/body/div[12]/div[2]/div/ul/li[{i}]/a")
            print(f"/html/body/section[3]/section/div[1]/div/div/div[1]/div/h2")
