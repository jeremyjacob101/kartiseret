from utils.logger import setup_logging

setup_logging()  # setup_logging("INFO") in CI if too chatty

from scraping.threading.scrape import main

if __name__ == "__main__":
    main()
