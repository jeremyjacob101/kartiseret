from datetime import datetime, date
from supabase import create_client
import os, re, unicodedata


def setUpSupabase(self):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    self.supabase = create_client(url, key)

def setUpOmdb(self):
    self.OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

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

        title = unicodedata.normalize("NFKD", title)
        title = title.encode("ascii", "ignore").decode("ascii")

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

    def upsertUpdates(self, table_name: str):
        if self.updates:
            self.supabase.table(table_name).upsert(self.updates).execute()
        self.updates = []

    def canonicalize_title(self, title):
        if not title:
            return ""

        t = unicodedata.normalize("NFKC", title.lower().strip())
        t = re.sub(r":\s*הסרט$", "", t)
        t = t.replace("-", " ")
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"[^\w\s\u0590-\u05FF]", "", t)
        t = re.sub(r"\bשנים\b", "שנה", t)
        t = t.replace(" ", "")

        return t

    def levenshtein_distance(self, a, b, max_distance=1):
        if a == b:
            return 0

        if abs(len(a) - len(b)) > max_distance:
            return max_distance + 1

        if len(a) == len(b):
            diffs = [i for i in range(len(a)) if a[i] != b[i]]
            if len(diffs) == 2:
                i, j = diffs
                if j == i + 1 and a[i] == b[j] and a[j] == b[i]:
                    return 1

        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            curr = [i]
            min_row = i
            for j, cb in enumerate(b, 1):
                cost = 0 if ca == cb else 1
                insert_cost = curr[j - 1] + 1
                delete_cost = prev[j] + 1
                replace_cost = prev[j - 1] + cost
                val = min(insert_cost, delete_cost, replace_cost)
                curr.append(val)
                min_row = min(min_row, val)
            if min_row > max_distance:
                return max_distance + 1
            prev = curr

        return prev[-1]

    def fuzzy_key(self, title, cache=None):
        canonical = self.canonicalize_title(title)
        if cache is None:
            return canonical
        if canonical in cache:
            return cache[canonical]

        for k in cache.keys():
            if self.levenshtein_distance(canonical, k, max_distance=1) <= 1:
                cache[canonical] = k
                return k

        cache[canonical] = canonical
        return canonical
