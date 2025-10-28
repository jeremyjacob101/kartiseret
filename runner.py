from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging, logger
import threading, time

from backend.scraping.chains.CinemaCity import CinemaCity
from backend.scraping.chains.YesPlanet import YesPlanet
from backend.scraping.chains.LevCinema import LevCinema
from backend.scraping.chains.RavHen import RavHen
from backend.scraping.chains.MovieLand import MovieLand
from backend.scraping.chains.HotCinema import HotCinema

from backend.scraping.cinematheques.JLEMtheque import JLEMtheque
from backend.scraping.cinematheques.SSCtheque import SSCtheque
from backend.scraping.cinematheques.JAFCtheque import JAFCtheque
from backend.scraping.cinematheques.HAIFtheque import HAIFtheque
from backend.scraping.cinematheques.HERZtheque import HERZtheque
from backend.scraping.cinematheques.TLVtheque import TLVtheque
from backend.scraping.cinematheques.HOLONtheque import HOLONtheque

from backend.scraping.comingsoons.CCsoon import CCsoon
from backend.scraping.comingsoons.HCsoon import HCsoon
from backend.scraping.comingsoons.LCsoon import LCsoon
from backend.scraping.comingsoons.MLsoon import MLsoon
from backend.scraping.comingsoons.YPsoon import YPsoon

from backend.dataflow.comingsoons.ComingSoonsData import find_3d_movies

REGISTRY = {
    "nowPlaying": [
        CinemaCity,
        YesPlanet,
        LevCinema,
        RavHen,
        MovieLand,
        HotCinema,
    ],
    "cinematheque": [
        JLEMtheque,
        SSCtheque,
        JAFCtheque,
        HAIFtheque,
        HERZtheque,
        TLVtheque,
        HOLONtheque,
    ],
    "comingSoon": [
        CCsoon,
        HCsoon,
        LCsoon,
        MLsoon,
        YPsoon,
    ],
}

TABLE_BY_TYPE = {
    "nowPlaying": "testingMovies",
    "cinematheque": "testingTheques",
    "comingSoon": "testingSoons",
}

ID_FIELD_BY_TYPE = {
    "nowPlaying": "showtime_id",
    "cinematheque": "theque_showtime_id",
    "comingSoon": "coming_soon_id",
}


def runCinemaType(type: str):
    setup_logging("ERROR")
    classes = REGISTRY.get(type, [])
    table_name = TABLE_BY_TYPE.get(type)
    id_field_name = ID_FIELD_BY_TYPE.get(type)

    threads, runtimes, lock = [], {}, threading.Lock()

    for cls in classes:

        def _target(c=cls):
            t0 = time.time()
            try:
                instance = c(cinema_type=type, supabase_table_name=table_name, id_name=id_field_name)
                instance.scrape()
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


def runDataLogic():
    find_3d_movies()


def main():
    runCinemaType("nowPlaying")
    runCinemaType("cinematheque")
    runCinemaType("comingSoon")

    runDataLogic()


if __name__ == "__main__":
    main()

# Finish cinematheques:
#
# Handle 3D / 3D HDR in titles (remove from ComingSoons, handle in NowPlayings)
# Skip russian titles throughout?
#

#########
#
# Finish above comments
#
# Add in OMDb logic
# Hook up to current front end
# Rewrite front end
#
