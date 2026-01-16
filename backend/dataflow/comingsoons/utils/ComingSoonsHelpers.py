from datetime import date
import re, unicodedata


class ComingSoonsHelpers:
    def comingSoonsSortKey(self, row):
        d_key = self.dateToDate(row.get("release_date"))
        runtime = row.get("runtime")
        good_runtime = (runtime is not None) and (runtime not in getattr(self, "fake_runtimes", set()))
        has_release_year = bool(row.get("release_year"))
        has_directed_by = bool((row.get("directed_by") or "").strip())

        return (
            d_key,
            0 if has_directed_by else 1,
            0 if good_runtime else 1,
            0 if has_release_year else 1,
        )

    def comingSoonsFinalDedupeSortKey(self, row):
        d_key = self.dateToDate(row.get("release_date"))

        heb = (row.get("hebrew_title") or "").strip()
        has_hebrew = bool(heb) and heb.lower() != "null"

        return (
            d_key,
            0 if has_hebrew else 1,
        )

    def comingSoonsFinalDedupeSortKey2(self, row: dict):
        rd = self.dateToDate(row["release_date"])
        ca_dt = self.datetimeToDatetime(row["created_at"])
        return (rd, -ca_dt.timestamp())

    def reset_soon_row_state(self):
        self.potential_chosen_id = None

        self.english_title = None
        self.hebrew_title = None
        self.release_date = None
        self.release_year = None
        self.directed_by = None
        self.runtime = None

        self.first_search_result = None
        self.found_year_match = False
        self.candidates = []
        self.details = {}

        self.seen_already = set()
        self.search_plans = []

    def load_soon_row(self, row: dict):
        def clean_str(v):
            return str(v) if v not in (None, "", "null") else ""

        def clean_int(v):
            try:
                return int(v) if v not in (None, "", "null") else None
            except:
                return None

        def clean_date(v):
            if v in (None, "", "null"):
                return None
            if isinstance(v, date):
                return v.isoformat()
            try:
                return date.fromisoformat(str(v)).isoformat()
            except ValueError:
                return None

        self.english_title = clean_str(row.get("english_title"))
        self.hebrew_title = clean_str(row.get("hebrew_title"))
        self.release_date = clean_date(row.get("release_date"))
        self.release_year = clean_int(row.get("release_year"))
        self.directed_by = clean_str(row.get("directed_by"))
        self.runtime = clean_int(row.get("runtime"))

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
