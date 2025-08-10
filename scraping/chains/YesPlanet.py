from scraping.chains.BaseCinema import BaseCinema


class YesPlanet(BaseCinema):
    NAME = "Yes Planet"
    URL = "https://www.planetcinema.co.il/?lang=en_GB#/"

    def logic(self, items):
        print(f"scraping yes planet")
