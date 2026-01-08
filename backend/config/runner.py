from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.utils import logger
from backend.utils.run_id import allocate_run_id
from backend.config.runners import runGroup
import os


def main():
    logger.setup_logging()
    run_id = allocate_run_id()

    runGroup("cinema", "testingSoons", run_id)
    runGroup("dataflow", "comingSoonsData", run_id)

    runGroup("cinema", "testingShowtimes", run_id)
    runGroup("dataflow", "nowPlayingData", run_id)

    # runGroup("cinema", "testingTheques", run_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        os._exit(0)
