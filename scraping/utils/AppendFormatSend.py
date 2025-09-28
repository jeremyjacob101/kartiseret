class AppendFormatSend:
    ID_FIELD_BY_TYPE = {
        "cinematheque": "theque_showtime_id",
        "comingSoon": "coming_soon_id",
        "nowPlaying": "showtime_id",
    }

    def appendToGatheringInfo(self):
        self.fixScreeningType()
        self.fixCinemaName()
        self.fixLanguage()
        self.fixRating()

        self.gathering_info["showtime"].append(self.showtime)
        self.gathering_info["english_title"].append(self.english_title)
        self.gathering_info["hebrew_title"].append(self.hebrew_title)
        self.gathering_info["english_href"].append(self.english_href)
        self.gathering_info["hebrew_href"].append(self.hebrew_href)
        self.gathering_info["screening_type"].append(self.screening_type)
        self.gathering_info["original_language"].append(self.original_language)
        self.gathering_info["dub_language"].append(self.dub_language)
        self.gathering_info["date_of_showing"].append(self.date_of_showing)
        self.gathering_info["release_year"].append(self.release_year)
        self.gathering_info["release_date"].append(self.release_date)
        self.gathering_info["directed_by"].append(self.directed_by)
        self.gathering_info["runtime"].append(self.runtime)
        self.gathering_info["rating"].append(self.rating)
        self.gathering_info["screening_city"].append(self.screening_city)
        self.gathering_info["helper_id"].append(self.helper_id)
        self.gathering_info["helper_type"].append(self.helper_type)
        self.gathering_info["scraped_at"].append(str(self.getJlemTimeNow()))
        self.gathering_info["cinema"].append(self.CINEMA_NAME)

        id_field = self.ID_FIELD_BY_TYPE.get(getattr(self, "cinema_type", None))
        if id_field:
            self.gathering_info.setdefault(id_field, []).append(str(self.getRandomHash()))

    def formatAndUpload(self, table_name=None):
        info = getattr(self, "gathering_info", {})
        if not isinstance(info, dict):
            return None

        active_columns = [name for name, values in info.items() if isinstance(values, list) and len(values) > 0]
        max_rows = max((len(info[name]) for name in active_columns), default=0)

        rows = []
        for row_index in range(max_rows):
            row_data = {}
            for column_name in active_columns:
                column_values = info[column_name]
                value = column_values[row_index] if row_index < len(column_values) else None
                if (isinstance(value, str) and (value := value.strip())) or (value is not None and (not hasattr(value, "__len__") or len(value) > 0)):
                    row_data[column_name] = value
            rows.append(row_data)

        table_name = getattr(self, "SUPABASE_TABLE_NAME", None)

        return self.supabase.table(table_name).insert(rows).execute()
