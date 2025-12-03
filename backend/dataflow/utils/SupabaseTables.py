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

    def deleteTheseRows(self, table_name: str):
        for i in range(0, len(self.delete_these), 200):
            chunk = self.delete_these[i : i + 200]
            self.supabase.table(table_name).delete().in_(self.PRIMARY_KEY, chunk).execute()
        self.delete_these = []

        attr_name = {
            self.MAIN_TABLE_NAME: "main_table_rows",
            self.DUPLICATE_TABLE_NAME: "duplicate_table_rows",
            self.MOVING_TO_TABLE_NAME: "moving_to_table_rows",
            self.HELPER_TABLE_NAME: "helper_table_rows",
        }.get(table_name)
        setattr(self, attr_name, self.selectAll(table_name))

    def upsertUpdates(self, table_name: str):
        if self.updates:
            self.supabase.table(table_name).upsert(self.updates).execute()
        self.updates = []
