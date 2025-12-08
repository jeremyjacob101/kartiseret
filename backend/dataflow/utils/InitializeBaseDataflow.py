from supabase import create_client
from openai import OpenAI
import os


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


def setUpOmdb(self):
    self.OMDB_API_KEY = os.environ.get("OMDB_API_KEY")


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
        self.reset_row_state()

        self.visited_already = set()
        self.delete_these = []
        self.updates = []
        self.PRIMARY_KEY = "id"

        self.fake_runtimes = [60, 90, 100, 120, 150, 180, 200, 240, 250]

    def reset_row_state(self):
        self.CHOSEN_IMDB_ID = None
        self.potential_chosen = None

        self.english_title = None
        self.directed_by = None
        self.release_year = None
        self.runtime = None

        self.first_search_result = None
        self.potential_imdb_ids = []
        self.details = {}

    def load_row(self, row: dict):
        self.reset_row_state()

        def clean_str(v):
            return str(v) if v not in (None, "", "null") else ""

        def clean_int(v):
            try:
                return int(v) if v not in (None, "", "null") else None
            except:
                return None

        self.english_title = clean_str(row.get("english_title"))
        self.directed_by = clean_str(row.get("directed_by"))
        self.release_year = clean_int(row.get("release_year"))
        self.runtime = clean_int(row.get("runtime"))
