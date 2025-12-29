from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils import logger
from utils.logger import setup_logging
from backend.config.runners import runGroup


def main():
    setup_logging()

    # runGroup("cinema", "testingSoons")
    # runGroup("cinema", "testingTheques")
    # runGroup("cinema", "testingShowtimes")

    # runGroup("dataflow", "comingSoonsData")
    # runGroup("dataflow", "nowPlayingData")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        pass
