from datetime import datetime, date
from supabase import create_client
import os, re


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


class DataflowHelpers:
    def selectAll(self, table: str, select: str = "*", batch_size: int = 1000) -> list[dict]:
        all_rows: list[dict] = []
        start = 0

        while True:
            end = start + batch_size - 1
            rows = self.supabase.table(table).select(select).range(start, end).execute().data or []
            all_rows.extend(rows)
            if len(rows) < batch_size:
                break
            start += batch_size

        return all_rows

    def removeBadTitle(self, title: str) -> bool:
        if not isinstance(title, str) or title.strip() == "":
            return True  # Empty
        if re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F]", title):
            return True  # Russian
        if re.search(r"[\u0590-\u05FF\uFB1D-\uFB4F]", title):
            return True  # Hebrew
        if "HOT CINEMA" in title:
            return True  # Cinema
        return False

    def normalizeTitle(self, title: str) -> str:
        if not isinstance(title, str):
            return ""
        title = title.lower()
        title = re.sub(r"[-–—:?!]+", " ", title)
        title = re.sub(r"[^a-z0-9 ]+", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title

    def dateToDate(self, v):
        if isinstance(v, date):
            return v
        return datetime.fromisoformat(str(v)).date()

    def deleteTheseRows(self):
        for i in range(0, len(self.delete_these), 200):
            chunk = self.delete_these[i : i + 200]
            self.supabase.table(self.TABLE_NAME).delete().in_(self.PRIMARY_KEY, chunk).execute()
        self.table_rows = self.selectAll(self.TABLE_NAME)
        self.delete_these = []
