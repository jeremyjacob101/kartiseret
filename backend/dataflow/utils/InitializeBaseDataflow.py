import os
from supabase import create_client


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


def setUpOmdb(self):
    self.OMDB_API_KEY = os.environ.get("OMDB_API_KEY")


class InitializeBaseDataflow:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.visited_already = set()
        self.delete_these = []
        self.updates = []
        self.PRIMARY_KEY = "id"

        self.potential_imdb_ids = []

        self.fake_runtimes = [60, 90, 100, 120, 150, 180, 200, 240, 250]
