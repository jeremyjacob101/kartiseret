from dotenv import load_dotenv

load_dotenv()

from datetime import date, timedelta
from supabase import create_client
import os


def clear_showtimes(days: int = 3):
    sb = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
    cutoff = (date.today() - timedelta(days=days)).isoformat()

    sb.table("testingShowtimes").delete().lt("date_of_showing", cutoff).execute()
    sb.table("testingFinalShowtimes").delete().lt("date_of_showing", cutoff).execute()


if __name__ == "__main__":
    clear_showtimes(days=3)
