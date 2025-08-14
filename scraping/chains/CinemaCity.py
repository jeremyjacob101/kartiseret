from scraping.chains.BaseCinema import BaseCinema


class CinemaCity(BaseCinema):
    CINEMA_NAME = "Cinema City"
    URL = "https://www.cinema-city.co.il/"

    def logic(self):
        print()
