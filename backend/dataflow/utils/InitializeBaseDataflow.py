from supabase import create_client
from openai import OpenAI
import os


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


def setUpOmdb(self):
    self.OMDB_API_KEY = os.environ.get("OMDB_API_KEY")


def setUpTmdb(self):
    self.TMDB_API_KEY = os.environ.get("TMDB_API_KEY")


def setUpOpenAI(self):
    self.OPENAI_TEST_KEY_2 = os.environ.get("OPENAI_TEST_KEY_2")
    self.OPENAI_TEST_ADMIN_KEY_2 = os.environ.get("OPENAI_TEST_ADMIN_KEY_2")

    key_to_use = self.OPENAI_TEST_KEY_2 or self.OPENAI_TEST_ADMIN_KEY_2
    if not key_to_use:
        raise RuntimeError("No OpenAI API key found in environment variables.")

    self.openAiClient = OpenAI(api_key=key_to_use)


class InitializeBaseDataflow:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_soon_row_state()

        self.non_deduplicated_updates = []
        self.non_enriched_updates = []
        self.visited_already = set()
        self.delete_these = []
        self.updates = []
        self.PRIMARY_KEY = "id"
        self.potential_chosen_id = None

        self.first_search_result = None
        self.found_year_match = False
        self.results_page = 1
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
        self.results_page = 1
        self.candidates = []
        self.details = {}
