from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)


def clear_testingSoonsHelpers():
    return sb.table("testingSoonsHelpers").delete().filter("id", "not.is", "null").execute()


if __name__ == "__main__":
    clear_testingSoonsHelpers()
