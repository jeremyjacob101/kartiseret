class SupabaseHelpers():
    def selectAll(self, table: str, select: str = "*", batch_size: int = 1000) -> list[dict]:
        all_rows: list[dict] = []
        start = 0

        while True:
            end = start + batch_size - 1
            resp = self.supabase.table(table).select(select).range(start, end).execute()
            rows = resp.data or []
            all_rows.extend(rows)
            if len(rows) < batch_size:
                break
            start += batch_size

        return all_rows