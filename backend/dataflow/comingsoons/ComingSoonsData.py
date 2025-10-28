from backend.dataflow.BaseSupabaseData import BaseSupabaseData
import re


class ComingSoonsData(BaseSupabaseData):
    TABLE_NAME = "testingSoons"
    PRIMARY_KEY = "coming_soon_id"

    def logic(self):
        rows = self.selectAll(self.TABLE_NAME)

        seen = set()
        delete_ids = []

        for row in rows:
            title = row.get("english_title")
            if not isinstance(title, str) or title.strip() == "" or bool(re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F]", title)):
                delete_ids.append(row[self.PRIMARY_KEY])
                continue

            

            key = self.normalizeTitle(title)
            if key in seen:
                delete_ids.append(row[self.PRIMARY_KEY])
            else:
                seen.add(key)

        for i in range(0, len(delete_ids), 200):
            chunk = delete_ids[i : i + 200]
            self.supabase.table(self.TABLE_NAME).delete().in_(self.PRIMARY_KEY, chunk).execute()
