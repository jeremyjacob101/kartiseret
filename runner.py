from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging, logger
import threading, time

# from scraping.chains.CinemaCity import CinemaCity
# from scraping.chains.YesPlanet import YesPlanet
# from scraping.chains.LevCinema import LevCinema
# from scraping.chains.RavHen import RavHen
# from scraping.chains.MovieLand import MovieLand
# from scraping.chains.HotCinema import HotCinema

# from scraping.comingsoons.CCsoon import CCsoon
# from scraping.comingsoons.HCsoon import HCsoon
from scraping.comingsoons.LCsoon import LCsoon
# from scraping.comingsoons.MLsoon import MLsoon
# from scraping.comingsoons.YPsoon import YPsoon

# from scraping.cinematheques.JLEMtheque import JLEMtheque

REGISTRY = {
    "nowPlaying": [
        # CinemaCity,
        # YesPlanet,
        # LevCinema,
        # RavHen,
        # MovieLand,
        # HotCinema,
    ],
    "comingSoon": [
        # CCsoon,
        # HCsoon,
        LCsoon,
        # MLsoon,
        # YPsoon,
    ],
    "cinematheque": [
        # JLEMtheque,
    ],
}

TABLE_BY_MODE = {
    "nowPlaying": "testingMovies",
    "comingSoon": "testingSoons",
    "cinematheque": "testingTheques",
}

ID_FIELD_BY_MODE = {
    "nowPlaying": "showtime_id",
    "comingSoon": "coming_soon_id",
    "cinematheque": "theque_showtime_id",
}

def run(mode: str):
    setup_logging("ERROR")
    classes = REGISTRY.get(mode, [])
    table_name = TABLE_BY_MODE.get(mode)
    id_field_name = ID_FIELD_BY_MODE.get(mode)

    threads, runtimes, lock = [], {}, threading.Lock()

    for cls in classes:

        def _target(c=cls):
            t0 = time.time()
            try:
                inst = c(cinema_type=mode, supabase_table_name=table_name, id_name=id_field_name)
                inst.scrape()
            except Exception:
                logger.exception("Unhandled error in %s", c.__name__)
                raise
            finally:
                dt = time.time() - t0
                with lock:
                    runtimes[c.__name__] = dt

        thread = threading.Thread(target=_target, name=cls.__name__)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n\n\n--------------------\n")
    for name, secs in runtimes.items():
        m, s = divmod(int(secs), 60)
        print(f"{name}: {m}m{s:02d}s\n")


def main():
    # run("nowPlaying")
    # run("cinematheque")
    run("comingSoon")


if __name__ == "__main__":
    main()

# handle 3D / 3D HDR in titles (remove from coming soons, handle in now playings)
# get rid of duplicates in comingsoons that only differ by coming_soon_id
# skip russian titles throughout?
