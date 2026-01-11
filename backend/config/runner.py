from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.config.runners import runGroup, runPlan, DEFAULT_PLAN
from backend.utils.console.inputMenu import choose_run_plan
from backend.utils.log import logger
import os


def main():
    logger.setup_logging()
    run_id = logger.allocate_run_id()

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
