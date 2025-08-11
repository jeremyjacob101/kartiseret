from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

import threading
from utils.logger import setup_logging

from scraping.chains.CinemaCity import CinemaCity
from scraping.chains.YesPlanet import YesPlanet
from scraping.chains.LevCinema import LevCinema


def worker(cinema_class):
    cinema = cinema_class()
    cinema.scrape()


def main():
    setup_logging("ERROR")

    cinemas = [CinemaCity, YesPlanet, LevCinema]
    threads = []

    for cinema in cinemas:
        thread = threading.Thread(target=worker, args=(cinema,), name=cinema.__name__)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
