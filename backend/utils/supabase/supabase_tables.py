from dotenv import load_dotenv

load_dotenv()

from typing import Optional, Sequence
from supabase import create_client
import os


sb = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))


def sync_tables(action: str, source_table: Optional[str] = None, target_tables: Optional[Sequence[str]] = None, page_size: int = 1000, start: int = 0) -> None:
    targets = list(target_tables or [])
    action = action.strip().lower()
    if action not in {"append", "clear", "replace"} or ((action in {"append", "replace"}) and not source_table) or not targets:
        raise ValueError("action must be one of: append, clear, replace OR no source_table when append/replace OR no target_tables")

    if action == "clear" or action == "replace":
        for target in targets:
            sb.table(target).delete().filter("id", "not.is", "null").execute()
        if action == "clear":
            return

    while True:
        res = sb.table(source_table).select("*").range(start, start + page_size - 1).execute()
        rows = res.data or []
        if not rows:
            break

        for target in targets:
            sb.table(target).insert(rows).execute()

        start += page_size


if __name__ == "__main__":  # append, clear, replace
    sync_tables(action="clear", source_table="testingShowtimes", target_tables=["testingShowtimes"])
