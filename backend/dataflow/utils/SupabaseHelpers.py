import re


class SupabaseHelpers:
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

    def removeNonEnglish(self, title: str):
        if not isinstance(title, str):
            return True

    def normalizeTitle(self, title: str) -> str:
        if not isinstance(title, str):
            return ""
        title = title.lower()
        title = re.sub(r"[-–—:?!]+", " ", title)
        title = re.sub(r"[^a-z0-9 ]+", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title
