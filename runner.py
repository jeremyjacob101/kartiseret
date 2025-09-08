from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging, logger, dump_artifacts
import threading
import time

from scraping.chains.CinemaCity import CinemaCity
from scraping.chains.YesPlanet import YesPlanet
from scraping.chains.LevCinema import LevCinema
from scraping.chains.RavHen import RavHen
from scraping.chains.MovieLand import MovieLand


def run_chains():
    cinemas = [
        # CinemaCity,
        # YesPlanet,
        LevCinema,
        # RavHen,
        # MovieLand,
    ]
    threads, runtimes, lock = [], {}, threading.Lock()

    for cinema in cinemas:

        def _target(cls=cinema):
            t0 = time.time()
            try:
                inst = cls()
                inst.scrape()
            except Exception:
                logger.exception("Unhandled error in %s", cls.__name__)
                raise
            finally:
                dt = time.time() - t0
                with lock:
                    runtimes[cls.__name__] = dt

        thread = threading.Thread(target=_target, name=cinema.__name__)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n\n\n--------------------\n")
    for name, secs in runtimes.items():
        m, s = divmod(int(secs), 60)
        print(f"{name}: {m}m{s:02d}s\n")


def main():
    setup_logging("ERROR")
    run_chains()


if __name__ == "__main__":
    main()

# maybe split up cinema city into three threads
