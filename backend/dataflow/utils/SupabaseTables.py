from typing import Callable, Any


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
        table_to_attr: dict[str, str] = {
            self.MAIN_TABLE_NAME: "main_table_rows",
            self.DUPLICATE_TABLE_NAME: "duplicate_table_rows",
            self.MOVING_TO_TABLE_NAME: "moving_to_table_rows",
            self.MOVING_TO_TABLE_NAME_2: "moving_to_table_2_rows",
            self.HELPER_TABLE_NAME: "helper_table_rows",
            self.HELPER_TABLE_NAME_2: "helper_table_2_rows",
            self.HELPER_TABLE_NAME_3: "helper_table_3_rows",
            self.HELPER_TABLE_NAME_4: "helper_table_4_rows",
        }

        if table_name:
            attr = table_to_attr.get(table_name)
            if attr:
                setattr(self, attr, self.selectAll(table_name))
            return

        for table, attr in table_to_attr.items():
            if table:
                setattr(self, attr, self.selectAll(table))

    def deleteTheseRows(self, table_name: str, primary_key: str = "id", refresh: bool = True):
        if not self.delete_these:
            return

        seen = set()
        deduped = []
        for x in self.delete_these:
            if x in (None, "", "null") or x in seen:
                continue
            seen.add(x)
            deduped.append(x)

        for i in range(0, len(deduped), 200):
            chunk = deduped[i : i + 200]
            self.supabase.table(table_name).delete().in_(primary_key, chunk).execute()
        self.delete_these = []
        if refresh:
            self.refreshAllTables(table_name)

    def upsertUpdates(self, table_name: str, refresh: bool = True):
        if self.updates:
            self.supabase.table(table_name).upsert(self.updates).execute()
        self.updates = []
        if refresh:
            self.refreshAllTables(table_name)

    def dedupeTable(self, table_name: str, id_col: str = "id", ignore_cols: set[str] | None = None, refresh: bool = True, sort_key: Callable[[dict], Any] | None = None, sort_reverse: bool = False):
        ignore = set(ignore_cols or set())
        ignore.update({id_col, "created_at", "scraped_at", "run_id", "old_uuid"})
        seen = set()

        if sort_key is None:
            sort_key = lambda r: r.get("created_at") or ""

        rows = self.selectAll(table_name)
        rows.sort(key=sort_key, reverse=True if sort_reverse else False)

        for row in rows:
            key = tuple(sorted((k, repr(v)) for k, v in row.items() if k not in ignore))
            if key in seen:
                self.delete_these.append(row.get(id_col))
            else:
                seen.add(key)

        if self.delete_these:
            self.deleteTheseRows(table_name, primary_key=id_col)
        if refresh:
            self.refreshAllTables(table_name)
