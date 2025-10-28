from backend.dataflow.BaseSupabaseData import BaseSupabaseData
import re


class ComingSoonsData(BaseSupabaseData):
    TABLE_NAME = "testingSoons"
    PRIMARY_KEY = "coming_soon_id"

    def logic(self):
        comingSoons = self.selectAll(self.TABLE_NAME)

        visited_already = set()
        delete_these = []

        for row in comingSoons:
            english_title = row.get("english_title")
            if self.removeBadTitle(english_title):
                delete_these.append(row[self.PRIMARY_KEY])
                continue

            normalizedTitle = self.normalizeTitle(english_title)
            if normalizedTitle in visited_already:
                delete_these.append(row[self.PRIMARY_KEY])
            else:
                visited_already.add(normalizedTitle)

        for i in range(0, len(delete_these), 200):
            chunk = delete_these[i : i + 200]
            self.supabase.table(self.TABLE_NAME).delete().in_(self.PRIMARY_KEY, chunk).execute()
