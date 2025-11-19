from backend.dataflow.BaseDataflowData import BaseDataflowData
from collections import defaultdict


class ComingSoonsData(BaseDataflowData):
    MAIN_TABLE_NAME = "testingSoons"
    HELPER_TABLE_NAME = "testingSoonsHelpers"

    def logic(self):
        for row in self.main_table_rows:
            row["english_title"] = self.normalizeTitle(row.get("english_title"))
            if self.removeBadTitle(row.get("english_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])

            self.updates.append({"id": row["id"], "english_title": row["english_title"]})

        self.upsertUpdates()
        self.deleteTheseRows(self.MAIN_TABLE_NAME)

        groups, helpers_by_winner = defaultdict(list), defaultdict(list)

        for row in self.main_table_rows:
            key = (row.get("english_title"), row.get("hebrew_title"))
            groups[key].append(row)

        for key, rows in groups.items():
            if len(rows) <= 1:
                continue
            winner = min(rows, key=self.comingSoonsSortKey)
            winner_id = winner[self.PRIMARY_KEY]

            winner_helper = winner.get("helper_id")
            if winner_helper:
                helpers_by_winner[winner_id].append(winner_helper)

            for r in rows:
                if r[self.PRIMARY_KEY] == winner_id:
                    continue

                self.delete_these.append(r[self.PRIMARY_KEY])
                helpers_by_winner[winner_id].append(r.get("helper_id"))

        self.comingSoonsWriteHelpers(helpers_by_winner)
        self.deleteTheseRows(self.MAIN_TABLE_NAME)
