from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)

start, PAGE_SIZE = 0, 1000


def append_testingSoons_to_testingSoons2():
    while True:
        res = sb.table("testingSoons").select("*").range(start, start + PAGE_SIZE - 1).execute()
        rows = res.data or []
        if not rows:
            break

        sb.table("testingSoons2").insert(rows).execute()
        start += PAGE_SIZE


if __name__ == "__main__":
    append_testingSoons_to_testingSoons2()
