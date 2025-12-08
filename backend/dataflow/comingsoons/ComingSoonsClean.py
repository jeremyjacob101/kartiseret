from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict


class ComingSoonsClean(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    HELPER_TABLE_NAME = "testingSoonsHelpers"

    def logic(self):
        for row in self.main_table_rows:
            row["english_title"] = self.normalizeTitle(row.get("english_title") or "")
            row["hebrew_title"] = (row.get("hebrew_title") or "").lower()
            if self.removeBadTitle(row.get("english_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])
            if self.removeRussianHebrewTitle(row.get("hebrew_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])

            self.updates.append({"id": row["id"], "english_title": row["english_title"], "hebrew_title": row.get("hebrew_title")})

        self.upsertUpdates(self.MAIN_TABLE_NAME)
        self.deleteTheseRows(self.MAIN_TABLE_NAME)

        groups, helpers_by_winner = defaultdict(list), defaultdict(list)

        fuzzy_cache = {}
        for row in self.main_table_rows:
            canon_eng = self.fuzzy_key(row["english_title"], cache=fuzzy_cache)
            canon_heb = self.fuzzy_key(row["hebrew_title"], cache=fuzzy_cache)
            key = (canon_eng, canon_heb)
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
        self.comingSoonsWriteSingleHelpers(groups)
        self.deleteTheseRows(self.MAIN_TABLE_NAME)
