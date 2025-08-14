from scraping.chains.BaseCinema import BaseCinema


class CinemaCity(BaseCinema):
    NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/"

    def logic(self):
        print()
