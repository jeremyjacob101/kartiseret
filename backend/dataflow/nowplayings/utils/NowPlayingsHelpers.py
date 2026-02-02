from datetime import datetime, date


class NowPlayingsHelpers:
    def applyYesPlanetHebrewToRavHenEnglish(self):
        yes_map = {}
        for row in self.main_table_rows:
            if row.get("cinema") == "Yes Planet":
                hebrew = (row.get("hebrew_title") or "").strip()
                english = (row.get("english_title") or "").strip()
                if hebrew and english and hebrew not in yes_map:
                    yes_map[hebrew] = english
        for row in self.main_table_rows:
            if row.get("cinema") == "Rav Hen":
                key = (row.get("english_title") or "").strip()
                if key in yes_map:
                    row["english_title"] = yes_map[key]

    def createdAtToDatetime(self, ca):
        if isinstance(ca, datetime):
            return ca
        s = str(ca).replace("T", " ")
        s = s[:-3] + "+0000"
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f%z")

    def newestCreatedAtSortKey(self, row: dict):
        return self.datetimeToDatetime(row["created_at"])

    def nowPlayingsGroupKey(self, normalized_title: str) -> str:
        t = (normalized_title or "").strip().lower()
        for prefix in ("the ", "a ", "an "):
            if t.startswith(prefix):
                t = t[len(prefix) :].strip()
                break
        return t

    def titleIsSkipped(self, title: str, skip_tokens: set) -> bool:
        title_raw = (title or "").strip().lower()
        try:
            title_norm = self.normalizeTitle(title or "").strip().lower()
        except:
            title_norm = title_raw
        return title_raw in skip_tokens or title_norm in skip_tokens

    def reset_np_main_row_state(self):
        self.english_title = None
        self.hebrew_title = None
        self.date_of_showing = None
        self.release_year = None
        self.directed_by = None
        self.runtime = None

        self.popularity = None
        self.tmdb_id = None
        self.tmdbRating = None
        self.tmdbVotes = None
        self.imdb_id = None
        self.imdbRating = None
        self.imdbVotes = None
        self.rt_id = None
        self.rtAudienceRating = None
        self.rtAudienceVotes = None
        self.rtCriticRating = None
        self.rtCriticVotes = None
        self.lb_id = None
        self.lbRating = None
        self.lbVotes = None
        self.poster = None
        self.backdrop = None

    def load_np_main_row(self, row: dict):
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
        self.date_of_showing = clean_date(row.get("date_of_showing"))
        self.release_year = clean_int(row.get("release_year"))
        self.directed_by = clean_str(row.get("directed_by"))
        self.runtime = clean_int(row.get("runtime"))

    def load_update_final_movies_main_row(self, row: dict):
        def clean_str(v):
            return str(v) if v not in (None, "", "null") else ""

        def clean_int(v):
            try:
                return int(v) if v not in (None, "", "null") else None
            except:
                return None

        def clean_float(v):
            try:
                return float(v) if v not in (None, "", "null") else None
            except:
                return None

        self.english_title = clean_str(row.get("english_title"))
        self.release_year = clean_int(row.get("release_year"))
        self.runtime = clean_int(row.get("runtime"))
        self.popularity = clean_float(row.get("popularity"))
        self.tmdb_id = clean_int(row.get("tmdb_id"))
        self.tmdbRating = clean_int(row.get("tmdbRating"))
        self.tmdbVotes = clean_int(row.get("tmdbVotes"))
        self.imdb_id = clean_str(row.get("imdb_id"))
        self.imdbRating = clean_float(row.get("imdbRating"))
        self.imdbVotes = clean_int(row.get("imdbVotes"))
        self.rt_id = clean_str(row.get("rt_id"))
        self.rtAudienceRating = clean_int(row.get("rtAudienceRating"))
        self.rtAudienceVotes = clean_int(row.get("rtAudienceVotes"))
        self.rtCriticRating = clean_int(row.get("rtCriticRating"))
        self.rtCriticVotes = clean_int(row.get("rtCriticVotes"))
        self.lb_id = clean_str(row.get("lb_id"))
        self.lbRating = clean_float(row.get("lbRating"))
        self.lbVotes = clean_int(row.get("lbVotes"))
        self.poster = clean_str(row.get("poster"))
        self.backdrop = clean_str(row.get("backdrop"))

    def reset_np_groupkey_row_state(self):
        self.potential_chosen_id = None
        self.candidates = []
        self.details = {}

        self.override_tmdb = None
        self.seen_already = set()
        self.search_plans = []

        self.parsed_year = None
        self.year_counts = {}

    def load_np_groupkey_meta_row(self, key):
        meta = self.meta_by_key.get(key) or {}
        self.hebrew_title = meta.get("hebrew_title")
        self.directed_by = meta.get("directed_by")
        self.runtime = meta.get("runtime")
        self.year_counts = meta.get("year_counts") or {}
        self.parsed_year = None
