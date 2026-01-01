import csv, json, pathlib, threading, time


def _format_rows_from_gathering_info(self):
    info = getattr(self, "gathering_info", {})
    if not isinstance(info, dict):
        return [], []

    active_columns = [name for name, values in info.items() if isinstance(values, list) and len(values) > 0]
    max_rows = max((len(info[name]) for name in active_columns), default=0)

    if not active_columns or max_rows == 0:
        return [], []

    rows = []
    for row_index in range(max_rows):
        row_data = {}
        for column_name in active_columns:
            column_values = info[column_name]
            value = column_values[row_index] if row_index < len(column_values) else None

            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    continue
            elif value is None:
                continue
            else:
                try:
                    if hasattr(value, "__len__") and len(value) == 0:
                        continue
                except Exception:
                    pass

            if isinstance(value, (dict, list, tuple, set)):
                value = json.dumps(value, ensure_ascii=False)

            row_data[column_name] = value

        if row_data:
            rows.append(row_data)

    return rows, active_columns


def formatAndWriteCsv(self, *, note: str = "gathering_info"):
    try:
        rows, columns = _format_rows_from_gathering_info(self)
        if not rows:
            return None

        artifact_dir = pathlib.Path("backend/utils/logger_artifacts")
        artifact_dir.mkdir(parents=True, exist_ok=True)

        name = getattr(self, "CINEMA_NAME", None) or self.__class__.__name__
        safe_prefix = str(name).replace(" ", "_")
        ts = time.strftime("%Y%m%d-%H%M%S")
        thread_name = threading.current_thread().name.replace(" ", "_")

        csv_path = artifact_dir / f"{safe_prefix}-{thread_name}-{ts}-{note}.csv"

        header = list(columns)
        if not header:
            keys = set()
            for r in rows:
                keys.update(r.keys())
            header = sorted(keys)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        self._last_csv_artifact = str(csv_path)
        return str(csv_path)
    except:
        pass


def formatAndUpload(self):
    rows, _columns = _format_rows_from_gathering_info(self)
    if not rows:
        raise Exception("Empty gathering_info table")
    return self.supabase.table(self.supabase_table_name).insert(rows).execute()


class AppendToInfo:
    def appendToGatheringInfo(self, print_info=False):
        self.fixScreeningType()
        self.fixScreeningTech()
        self.fixCinemaName()
        self.fixLanguage()
        self.fixRating()

        self.gathering_info["showtime"].append(self.showtime)
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["english_href"].append(self.english_href)
        self.gathering_info["hebrew_href"].append(self.hebrew_href)
        self.gathering_info["screening_type"].append(self.screening_type)
        self.gathering_info["screening_tech"].append(self.screening_tech)
        self.gathering_info["original_language"].append(self.original_language)
        self.gathering_info["dub_language"].append(self.dub_language)
        self.gathering_info["date_of_showing"].append(self.date_of_showing)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["release_date"].append(self.release_date)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["cinema"].append(self.CINEMA_NAME)

        if print_info:
            self.printRow()
