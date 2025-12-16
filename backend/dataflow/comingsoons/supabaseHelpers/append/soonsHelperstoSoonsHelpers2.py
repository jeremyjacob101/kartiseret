from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)


def append_testingSoonsHelpers_to_testingSoonsHelpers2():
    start, PAGE_SIZE = 0, 1000

    while True:
        res = sb.table("testingSoonsHelpers").select("*").range(start, start + PAGE_SIZE - 1).execute()
        rows = res.data or []
        if not rows:
            break

        sb.table("testingSoonsHelpers2").insert(rows).execute()
        start += PAGE_SIZE


if __name__ == "__main__":
    append_testingSoonsHelpers_to_testingSoonsHelpers2()
