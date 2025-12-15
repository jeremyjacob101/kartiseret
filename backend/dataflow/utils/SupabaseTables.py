class SupabaseTables:
    def selectAll(self, table: str, select: str = "*", batch_size: int = 1000) -> list[dict]:
        if not table:
            return []

        all_rows: list[dict] = []
        start = 0

        while True:
            end = start + batch_size - 1
            rows = self.supabase.table(table).select(select).range(start, end).execute().data or []
            all_rows.extend(rows)
            if len(rows) < batch_size:
                break
            start += batch_size

        return all_rows

    def refreshAllTables(self, table_name: str | None = None):
        table_to_attr = {
            self.MAIN_TABLE_NAME: "main_table_rows",
            self.DUPLICATE_TABLE_NAME: "duplicate_table_rows",
            self.MOVING_TO_TABLE_NAME: "moving_to_table_rows",
            self.MOVING_TO_TABLE_NAME_2: "moving_to_table_2_rows",
            self.HELPER_TABLE_NAME: "helper_table_rows",
            self.HELPER_TABLE_NAME_2: "helper_table_2_rows",
            self.HELPER_TABLE_NAME_3: "helper_table_3_rows",
        }
        if table_name:
            attr = table_to_attr.get(table_name)
            setattr(self, attr, self.selectAll(table_name))
            return
        for table, attr in table_to_attr.items():
            setattr(self, attr, self.selectAll(table))

    def deleteTheseRows(self, table_name: str, primary_key: str = "id"):
        for i in range(0, len(self.delete_these), 200):
            chunk = self.delete_these[i : i + 200]
            self.supabase.table(table_name).delete().in_(primary_key, chunk).execute()
        self.delete_these = []

        attr_name = {
            self.MAIN_TABLE_NAME: "main_table_rows",
            self.DUPLICATE_TABLE_NAME: "duplicate_table_rows",
            self.MOVING_TO_TABLE_NAME: "moving_to_table_rows",
            self.HELPER_TABLE_NAME: "helper_table_rows",
            self.HELPER_TABLE_NAME_2: "helper_table_2_rows",
            self.HELPER_TABLE_NAME_3: "helper_table_3_rows",
        }.get(table_name)
        setattr(self, attr_name, self.selectAll(table_name))

    def upsertUpdates(self, table_name: str):
        if self.updates:
            self.supabase.table(table_name).upsert(self.updates).execute()
        self.updates = []
        self.refreshAllTables(table_name)
