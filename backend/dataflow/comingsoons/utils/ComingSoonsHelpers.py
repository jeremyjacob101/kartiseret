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

    def comingSoonsWriteHelpers(self, helpers_by_winner: dict[str, list[str]]) -> None:
        for winner_id, new_helpers in helpers_by_winner.items():
            if not new_helpers:
                continue

            existing = self.supabase.table(self.HELPER_TABLE_NAME).select("*").eq("old_uuid", winner_id).execute()
            data = existing.data or []
            row = (data[0] if data else None) or {"old_uuid": winner_id}

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
                existing_values.add(helper_id)
                next_slot += 1

            self.updates.append(row)
        self.upsertUpdates(self.HELPER_TABLE_NAME)

    def comingSoonsWriteSingleHelpers(self, groups) -> None:
        existing = self.supabase.table(self.HELPER_TABLE_NAME).select("old_uuid").execute().data or []
        existing_ids = {row.get("old_uuid") for row in existing if row.get("old_uuid")}

        for rows in groups.values():
            if len(rows) != 1:
                continue

            row = rows[0]
            rid = row[self.PRIMARY_KEY]
            if rid in existing_ids:
                continue

            payload = {"old_uuid": rid}
            helper = row.get("helper_id")
            if helper not in (None, "", "null"):
                payload["helper_1"] = helper

            self.updates.append(payload)
        self.upsertUpdates(self.HELPER_TABLE_NAME)

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
