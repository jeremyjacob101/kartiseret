from datetime import date


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
