from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils import logger
from utils.logger import setup_logging
from localRunners import runCinemaType, runDataflows


def main():
    setup_logging("ERROR")

    # runCinemaType("testingSoons")
    # runCinemaType("testingTheques")
    # runCinemaType("testingShowtimes")

    # runDataflows("comingSoonsData")
    # runDataflows("nowPlayingData")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        pass
