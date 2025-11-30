from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from utils.logger import setup_logging
from backend.config.runners import runCinemaType, runDataflows


def main():
    setup_logging("ERROR")

    runCinemaType("testingMovies")
    runCinemaType("testingTheques")
    runCinemaType("testingSoons")

    # runDataflows()


if __name__ == "__main__":
    main()
