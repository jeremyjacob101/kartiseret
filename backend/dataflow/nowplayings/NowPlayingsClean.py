from backend.dataflow.BaseDataflow import BaseDataflow


class NowPlayingsClean(BaseDataflow):
    MAIN_TABLE_NAME = "testingShowtimes"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)

        self.applyYesPlanetHebrewToRavHenEnglish()

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
        self.dedupeTable(self.MAIN_TABLE_NAME, ignore_cols={"id", "created_at", "run_id", "release_year", "hebrew_title", "hebrew_href", "english_href", "scraped_at", "rating", "directed_by", "runtime", "tmdb_id", "cleaned"}, sort_key=lambda row: self.datetimeToDatetime(row["created_at"]), sort_reverse=True)
