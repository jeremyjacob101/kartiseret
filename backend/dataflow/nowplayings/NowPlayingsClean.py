from backend.dataflow.BaseDataflow import BaseDataflow


class NowPlayingsClean(BaseDataflow):
    MAIN_TABLE_NAME = "testingShowtimes"

    def logic(self):
        yes_map = {}
        # Move Yes Planet hebrew_titles into Rav Hen english_titles
        #
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
            #
            # Move Yes Planet hebrew_titles into Rav Hen english_titles

            row["english_title"] = self.normalizeTitle(row.get("english_title") or "")
            row["hebrew_title"] = (row.get("hebrew_title") or "").lower()

            if self.removeBadTitle(row.get("english_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])
            if self.removeRussianHebrewTitle(row.get("hebrew_title")):
                self.delete_these.append(row[self.PRIMARY_KEY])

            self.updates.append({"id": row["id"], "english_title": row["english_title"], "hebrew_title": row.get("hebrew_title")})

        self.upsertUpdates(self.MAIN_TABLE_NAME)
        self.deleteTheseRows(self.MAIN_TABLE_NAME)
