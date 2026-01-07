class NowPlayingsHelpers:
    def applyYesPlanetHebrewToRavHenEnglish(self):
        yes_map = {}
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
