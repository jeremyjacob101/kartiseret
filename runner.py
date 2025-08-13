from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging
from functools import partial
import threading

from scraping.chains.CinemaCity import CinemaCity
from scraping.chains.YesPlanet import YesPlanet
from scraping.chains.LevCinema import LevCinema


def run_chains():
    cinemas = [
        # CinemaCity,
        YesPlanet,
        # LevCinema,
    ]
    threads = []

    for cinema in cinemas:
        thread = threading.Thread(target=partial(cinema().scrape), name=cinema.__name__)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def main():
    setup_logging("ERROR")
    run_chains()


if __name__ == "__main__":
    main()
