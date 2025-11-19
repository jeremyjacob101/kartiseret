from backend.dataflow.BaseDataflowData import BaseDataflowData
from collections import defaultdict


class ComingSoonsData(BaseDataflowData):
    STARTING_TABLE_NAME = "testingSoons"
    HELPER_TABLE_NAME = "testingSoonsHelpers"

    def _comingSoonsFirstSortKey(self, row):
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

    def _write_helpers(self, helpers_by_winner: dict[str, list[str]]) -> None:
        for winner_id, new_helpers in helpers_by_winner.items():
            if not new_helpers:
                continue

            existing = self.supabase.table(self.HELPER_TABLE_NAME).select("*").eq("id", winner_id).maybe_single().execute()
            row = existing.data or {"id": winner_id}
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

    def logic(self):
        for row in self.starting_table_rows:
            english_title = row.get("english_title")
            if self.removeBadTitle(english_title):
                self.delete_these.append(row[self.PRIMARY_KEY])

        self.deleteTheseRows(self.STARTING_TABLE_NAME)

        groups, helpers_by_winner = defaultdict(list), defaultdict(list)

        for row in self.starting_table_rows:
            key = (row.get("english_title"), row.get("hebrew_title"), row.get("cinema"))
            groups[key].append(row)

        for key, rows in groups.items():
            if len(rows) <= 1:
                continue
            winner = min(rows, key=self._comingSoonsFirstSortKey)
            winner_id = winner[self.PRIMARY_KEY]

            winner_helper = winner.get("helper_id")
            if winner_helper:
                helpers_by_winner[winner_id].append(winner_helper)

            for r in rows:
                if r[self.PRIMARY_KEY] == winner_id:
                    continue

                self.delete_these.append(r[self.PRIMARY_KEY])

                helper_id = r.get("helper_id")
                if helper_id:
                    helpers_by_winner[winner_id].append(helper_id)

        self._write_helpers(helpers_by_winner)
        self.deleteTheseRows(self.STARTING_TABLE_NAME)

        ### PER CINEMA ADDITIONAL TIE-BREAKS

        # Cinema City

        # Yes Planet
        # Rav Hen
        # Hot Cinema
        # Movie Land
        # Lev Cinema

        ### All Cinemas

        normalizedEnglishTitle = self.normalizeTitle(english_title)
