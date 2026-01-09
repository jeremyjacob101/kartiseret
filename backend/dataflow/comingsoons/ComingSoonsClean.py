from backend.dataflow.BaseDataflow import BaseDataflow
from collections import defaultdict


class ComingSoonsClean(BaseDataflow):
    MAIN_TABLE_NAME = "allSoons"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)

        for row in self.main_table_rows:
            if row.get("cleaned") is True:
                continue
            row["english_title"] = self.normalizeTitle(row.get("english_title") or "")
            row["hebrew_title"] = (row.get("hebrew_title") or "").lower()
            if self.removeBadTitle(row.get("english_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])
            if self.removeRussianHebrewTitle(row.get("hebrew_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])
            self.updates.append({"id": row["id"], "english_title": row["english_title"], "hebrew_title": row.get("hebrew_title"), "cleaned": True})

        self.upsertUpdates(self.MAIN_TABLE_NAME, refresh=False)
        self.deleteTheseRows(self.MAIN_TABLE_NAME, refresh=False)
        self.dedupeTable(self.MAIN_TABLE_NAME)

        groups, fuzzy_cache = defaultdict(list), {}
        for row in self.main_table_rows:
            canon_eng = self.fuzzy_key(row["english_title"], cache=fuzzy_cache)
            canon_heb = self.fuzzy_key(row["hebrew_title"], cache=fuzzy_cache)
            groups[(canon_eng, canon_heb)].append(row)

        for _, rows in groups.items():
            if len(rows) <= 1:
                continue
            winner = min(rows, key=self.comingSoonsSortKey)
            winner_id = winner[self.PRIMARY_KEY]

            for r in rows:
                if r[self.PRIMARY_KEY] != winner_id:
                    self.delete_these.append(r[self.PRIMARY_KEY])

        self.deleteTheseRows(self.MAIN_TABLE_NAME, refresh=False)
        self.dedupeTable(self.MAIN_TABLE_NAME, refresh=False)
