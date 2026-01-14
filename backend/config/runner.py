from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.config.runners import runGroup, runPlan, DEFAULT_PLAN
from backend.utils.console.inputMenu import choose_run_plan
from backend.utils.log import logger
import os


def main():
    logger.setup_logging()
    with logger.RunLogSession() as run:
        if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("JJ_INTEL_MAC_WEEKLY_RUN") == "true":  # GH or Weekly-Shell Run
            run.run_groups(list(DEFAULT_PLAN), run_group_fn=runGroup)
        else:  # Present Local Run
            plan, header = choose_run_plan()
            run.set_plan(plan)

            ok = runPlan(run.run_id, plan, header_renderable=header)
            run.set_successful(ok)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.SUPPRESS_ERRORS = True
        os._exit(0)
