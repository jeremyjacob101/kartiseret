from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.utils import logger
from backend.utils.run_id import allocate_run_id
from backend.config.runners2 import runGroup, runPlan
from backend.utils.rich_readchar.rich_readchar_menu import choose_run_plan
import os
import sys


DEFAULT_PLAN: list[tuple[str, str]] = [
    ("cinema", "testingSoons"),
    ("dataflow", "comingSoonsData"),
    ("cinema", "testingShowtimes"),
    ("dataflow", "nowPlayingData"),
    # ("cinema", "testingTheques"),
]


def main():
    logger.setup_logging()
    run_id = allocate_run_id()

    running_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    is_tty = bool(getattr(sys.stdin, "isatty", lambda: False)())

    if running_github_actions or not is_tty:
        for kind, key in DEFAULT_PLAN:
            runGroup(kind, key, run_id)
        return

    plan, header = choose_run_plan()
    runPlan(plan, run_id, header_renderable=header)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        os._exit(0)
