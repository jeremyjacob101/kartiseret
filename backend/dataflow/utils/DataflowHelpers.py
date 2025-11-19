from datetime import datetime, date
from supabase import create_client
import os, re


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)


class DataflowHelpers:
    def selectAll(self, table: str, select: str = "*", batch_size: int = 1000) -> list[dict]:
        if not table:
            return []

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
        title = re.sub(r"[-–—:?!&]+", " ", title)
        title = re.sub(r"[^a-z0-9 ]+", "", title)
        title = re.sub(r"\s+", " ", title)
        return title.strip()

    def dateToDate(self, v):
        if isinstance(v, date):
            return v
        return datetime.fromisoformat(str(v)).date()

    def deleteTheseRows(self, table_name: str):
        for i in range(0, len(self.delete_these), 200):
            chunk = self.delete_these[i : i + 200]
            self.supabase.table(table_name).delete().in_(self.PRIMARY_KEY, chunk).execute()
        self.delete_these = []

        attr_name = {
            self.MAIN_TABLE_NAME: "main_table_rows",
            self.DUPLICATE_TABLE_NAME: "duplicate_table_rows",
            self.MOVING_TO_TABLE_NAME: "moving_to_table_rows",
            self.HELPER_TABLE_NAME: "helper_table_rows",
        }.get(table_name)
        setattr(self, attr_name, self.selectAll(table_name))

    def comingSoonsSortKey(self, row):
        d_key = self.dateToDate(row.get("release_date"))
        runtime = row.get("runtime")
        good_runtime = (runtime is not None) and (runtime not in getattr(self, "fake_runtimes", set()))
        has_release_year = bool(row.get("release_year"))
        has_directed_by = bool((row.get("directed_by") or "").strip())

        return (
            d_key,
            0 if good_runtime else 1,
            0 if has_release_year else 1,
            0 if has_directed_by else 1,
        )

    def comingSoonsWriteHelpers(self, helpers_by_winner: dict[str, list[str]]) -> None:
        for winner_id, new_helpers in helpers_by_winner.items():
            if not new_helpers:
                continue

            existing = self.supabase.table(self.HELPER_TABLE_NAME).select("*").eq("id", winner_id).execute()
            data = existing.data or []
            row = (data[0] if data else None) or {"id": winner_id}

            existing_values = {v for k, v in row.items() if k.startswith("helper_") and v not in (None, "", "null")}

            next_slot = 1
            while next_slot <= 20 and row.get(f"helper_{next_slot}") not in (None, "", "null"):
                next_slot += 1

            for helper_id in new_helpers:
                if helper_id in existing_values:
                    continue
                if next_slot > 20:
                    break
                row[f"helper_{next_slot}"] = helper_id
                next_slot += 1

            self.supabase.table(self.HELPER_TABLE_NAME).upsert(row).execute()

    def upsertUpdates(self):
        if self.updates:
            self.supabase.table(self.MAIN_TABLE_NAME).upsert(self.updates).execute()
        self.updates = []
