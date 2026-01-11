from dotenv import load_dotenv

load_dotenv()  # Load dotenv BEFORE importing anything that uses env vars

from backend.config.runners import runGroup, runPlan, DEFAULT_PLAN
from backend.utils.console.inputMenu import choose_run_plan
from backend.utils.supabase.run_id import allocate_run_id
from backend.utils.log import logger
import os


def main():
    logger.setup_logging()
    run_id = allocate_run_id()

    import os, re

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    print("SUPABASE_URL present:", bool(url), flush=True)
    print("SUPABASE_URL:", url, flush=True)
    print("SUPABASE_SERVICE_ROLE_KEY present:", bool(key), flush=True)
    print("SUPABASE_SERVICE_ROLE_KEY length:", len(key), flush=True)
    print("SUPABASE_SERVICE_ROLE_KEY has whitespace:", bool(re.search(r"\s", key)), flush=True)
    print("SUPABASE_SERVICE_ROLE_KEY startswith eyJ:", key.startswith("eyJ"), flush=True)

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
