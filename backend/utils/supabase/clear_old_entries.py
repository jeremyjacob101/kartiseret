from dotenv import load_dotenv

load_dotenv()

from datetime import date, timedelta
from supabase import create_client
import os


def clear_showtimes(days: int = 3, soons_days: int = 7, movies_days: int = 30):
    sb = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

    showtimes_cutoff = (date.today() - timedelta(days=days)).isoformat()
    soons_cutoff = (date.today() - timedelta(days=soons_days)).isoformat()
    final_movies_cutoff = (date.today() - timedelta(days=movies_days)).isoformat()

    sb.table("testingShowtimes").delete().lt("date_of_showing", showtimes_cutoff).execute()
    sb.table("testingFinalShowtimes").delete().lt("date_of_showing", showtimes_cutoff).execute()

    sb.table("testingSoons").delete().lt("release_date", soons_cutoff).execute()
    sb.table("testingFinalSoons").delete().lt("release_date", soons_cutoff).execute()

    sb.table("testingFinalMovies").delete().lt("created_at", final_movies_cutoff).execute()


if __name__ == "__main__":
    clear_showtimes(days=3, soons_days=7, movies_days=30)
