from backend.dataflow.BaseDataflow import BaseDataflow


class NowPlayingsClean(BaseDataflow):
    MAIN_TABLE_NAME = "testingShowtimes"

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
