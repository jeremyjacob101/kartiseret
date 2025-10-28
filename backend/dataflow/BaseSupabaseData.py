from utils.logger import artifactPrinting
from supabase import create_client
import os


from backend.dataflow.utils.SupabaseHelpers import SupabaseHelpers

def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


class BaseSupabaseData(SupabaseHelpers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def logic(self):
        raise NotImplementedError("Each cinema must implement its own logic()")

    def dataRun(self):
        try:
            setUpSupabase(self)  # Sets up supabase client for each cinema
            self.logic()  # Scraping logic
        except Exception:
            artifactPrinting(self)
            raise
