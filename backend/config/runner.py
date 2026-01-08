from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.utils import logger
from backend.utils.logger import setup_logging
# from backend.config.runners import runGroup
from backend.config.runners_new import runGroup
from backend.utils.run_id import allocate_run_id


def main():
    setup_logging()
    run_id = allocate_run_id()
    
    runGroup("cinema", "testingSoons", run_id)
    # runGroup("cinema", "testingTheques", run_id)
    runGroup("cinema", "testingShowtimes", run_id)

    runGroup("dataflow", "comingSoonsData", run_id)
    runGroup("dataflow", "nowPlayingData", run_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        pass
