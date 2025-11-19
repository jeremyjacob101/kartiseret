from backend.dataflow.BaseDataflowData import BaseDataflowData
from collections import defaultdict


class ComingSoonsData(BaseDataflowData):
    STARTING_TABLE_NAME = "testingSoons"

    def comingSoonsFirstSortKey(self, row):
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

    def logic(self):
        for row in self.starting_table_rows:
            english_title = row.get("english_title")
            if self.removeBadTitle(english_title):
                self.delete_these.append(row[self.PRIMARY_KEY])

        self.deleteTheseRows(self.STARTING_TABLE_NAME)

        groups = defaultdict(list)
        for row in self.starting_table_rows:
            key = (row.get("english_title"), row.get("hebrew_title"), row.get("cinema"))
            groups[key].append(row)

        for key, rows in groups.items():
            if len(rows) <= 1:
                continue
            winner = min(rows, key=self.comingSoonsFirstSortKey)
            winner_id = winner[self.PRIMARY_KEY]
            for r in rows:
                if r[self.PRIMARY_KEY] != winner_id:
                    self.delete_these.append(r[self.PRIMARY_KEY])

        self.deleteTheseRows(self.STARTING_TABLE_NAME)

        ### PER CINEMA

        # Cinema City

        # Yes Planet
        # Rav Hen
        # Hot Cinema
        # Movie Land
        # Lev Cinema

        ### All Cinemas

        normalizedEnglishTitle = self.normalizeTitle(english_title)
