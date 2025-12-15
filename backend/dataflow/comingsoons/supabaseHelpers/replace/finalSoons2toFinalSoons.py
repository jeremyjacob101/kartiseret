from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)

sb.table("testingFinalSoons").delete().filter("imdb_id", "not.is", "null").execute()

start, PAGE_SIZE = 0, 1000


def replace_testingFinalSoons2_to_testingFinalSoons():
    while True:
        res = sb.table("testingFinalSoons2").select("*").range(start, start + PAGE_SIZE - 1).execute()
        rows = res.data or []
        if not rows:
            break

        sb.table("testingFinalSoons").insert(rows).execute()
        start += PAGE_SIZE


if __name__ == "__main__":
    replace_testingFinalSoons2_to_testingFinalSoons()
