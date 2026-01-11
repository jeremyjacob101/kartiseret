from supabase import create_client
import time, os

runningGithubActions = os.environ.get("GITHUB_ACTIONS") == "true"
RUNNER_MACHINE = os.environ.get("RUNNER_MACHINE")


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


def setUpTmdb(self):
    self.TMDB_API_KEY = os.environ.get("TMDB_API_KEY")


def logSuccessfulRun(self) -> None:
    if not runningGithubActions:
        duration_seconds = time.perf_counter() - self.startTime
        avg_time_col, num_runs_col = "avg_time_" + str(RUNNER_MACHINE), "num_runs_" + str(RUNNER_MACHINE)

        resp = self.supabase.table("utilAvgTime").select(f"{avg_time_col},{num_runs_col}").eq("name", self.__class__.__name__).limit(1).execute()
        row = resp.data[0]
        old_avg = float(row.get(avg_time_col) or 0.0)
        n = int(row.get(num_runs_col) or 0)
        new_avg = (old_avg * n + float(duration_seconds)) / (n + 1)
        update_payload = {avg_time_col: float(new_avg), num_runs_col: n + 1}

        self.supabase.table("utilAvgTime").update(update_payload).eq("name", self.__class__.__name__).eq(num_runs_col, n).execute()


class InitializeBaseDataflow:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_soon_row_state()

        self.startTime = time.perf_counter()

        self.non_deduplicated_updates = []
        self.non_enriched_updates = []
        self.visited_already = set()
        self.delete_these = []
        self.updates = []
        self.PRIMARY_KEY = "id"
        self.potential_chosen_id = None

        self.first_search_result = None
        self.found_year_match = False
        self.candidates = []
        self.details = {}

        self.fake_runtimes = [0, 30, 40, 45, 60, 90, 100, 120, 130, 150, 180, 200, 240, 250, 300]

    def reset_soon_row_state(self):
        self.potential_chosen_id = None

        self.english_title = None
        self.hebrew_title = None
        self.release_date = None
        self.release_year = None
        self.directed_by = None
        self.runtime = None

        self.first_search_result = None
        self.found_year_match = False
        self.candidates = []
        self.details = {}
