from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)


def clear_testingFinalMovies2():
    return sb.table("testingFinalMovies2").delete().filter("tmdb_id", "not.is", "null").execute()


if __name__ == "__main__":
    clear_testingFinalMovies2()
