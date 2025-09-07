from scraping.chains.BaseCinema import BaseCinema

from datetime import datetime
import re


class MovieLand(BaseCinema):
    CINEMA_NAME = "MovieLand"
    URL = "https://movieland.co.il/"

    def logic(self):
        print(f"\nMovieland\n")
