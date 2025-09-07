from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging
from functools import partial
import threading
import time

from scraping.chains.CinemaCity import CinemaCity
from scraping.chains.YesPlanet import YesPlanet
from scraping.chains.LevCinema import LevCinema
from scraping.chains.RavHen import RavHen


def run_chains():
    cinemas = [
        # CinemaCity,
        YesPlanet,
        # LevCinema,
        # RavHen,
    ]
    threads, runtimes = [], {}

    for cinema in cinemas:
        start = time.time()
        thread = threading.Thread(target=partial(cinema().scrape), name=cinema.__name__)
        threads.append((cinema.__name__, thread, start))
        thread.start()

    for name, thread, start in threads:
        thread.join()
        duration = time.time() - start
        runtimes[name] = duration

    print("\n\n\n--------------------\n")
    for name, secs in runtimes.items():
        m, s = divmod(int(secs), 60)
        print(f"{name}: {m}m{s:02d}s\n")


def main():
    setup_logging("ERROR")
    run_chains()


if __name__ == "__main__":
    main()
