from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.utils import logger
from backend.utils.run_id import allocate_run_id
from backend.config.runners2 import runGroup, runPlan
from backend.utils.rich_readchar.rich_runInputMenu import choose_run_plan
import os
import sys


DEFAULT_PLAN: list[tuple[str, str]] = [
    ("cinema", "testingSoons"),
    ("cinema", "testingShowtimes"),
    ("dataflow", "comingSoonsData"),
    ("dataflow", "nowPlayingData"),
    # ("cinema", "testingTheques"),
]


def main():
    logger.setup_logging()
    run_id = allocate_run_id()

    if os.environ.get("GITHUB_ACTIONS") == "true":
        for kind, key in DEFAULT_PLAN:
            runGroup(kind, key, run_id)
        return

    runPlan(run_id, *choose_run_plan())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        os._exit(0)
