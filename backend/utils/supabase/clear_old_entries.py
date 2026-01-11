from dotenv import load_dotenv

load_dotenv()

from datetime import date, timedelta
from supabase import create_client
import os

SHOWTIMES_DAYS_BACK_FROM_TODAY_TO_REMOVE = 3
MOVIES_DAYS_BACK_FROM_TODAY_TO_REMOVE = 30
SOONS_DAYS_BACK_FROM_TODAY_TO_REMOVE = 7


def clear_showtimes(days, movies_days, soons_days):
    sb = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

    showtimes_cutoff = (date.today() - timedelta(days=days)).isoformat()
    soons_cutoff = (date.today() - timedelta(days=soons_days)).isoformat()
    final_movies_cutoff = (date.today() - timedelta(days=movies_days)).isoformat()

    sb.table("allShowtimes").delete().lt("date_of_showing", showtimes_cutoff).execute()
    sb.table("finalShowtimes").delete().lt("date_of_showing", showtimes_cutoff).execute()

    sb.table("finalMovies").delete().lt("created_at", final_movies_cutoff).execute()

    sb.table("allSoons").delete().lt("release_date", soons_cutoff).execute()
    sb.table("finalSoons").delete().lt("release_date", soons_cutoff).execute()


if __name__ == "__main__":
    clear_showtimes(days=SHOWTIMES_DAYS_BACK_FROM_TODAY_TO_REMOVE, movies_days=MOVIES_DAYS_BACK_FROM_TODAY_TO_REMOVE, soons_days=SOONS_DAYS_BACK_FROM_TODAY_TO_REMOVE)
