from typing import Callable, Any


class SupabaseTables:
    def selectAll(self, table: str, select: str = "*", batch_size: int = 200) -> list[dict]:
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
            if refresh:
                self.refreshAllTables(table_name)
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
            for row in self.updates:
                if isinstance(row, dict) and "run_id" not in row:
                    row["run_id"] = int(self.run_id)
            self.supabase.table(table_name).upsert(self.updates).execute()
        self.updates = []
        if refresh:
            self.refreshAllTables(table_name)

    def dedupeTable(self, table_name: str, id_col: str = "id", ignore_cols: set[str] | None = None, refresh: bool = True, sort_key: Callable[[dict], Any] | None = None, sort_reverse: bool = False, dedupe_added: bool = True):

        ########

        def _mask_id(x, keep=6):
            s = str(x)
            if len(s) <= keep * 2:
                return s
            return f"{s[:keep]}…{s[-keep:]}"

        def _type_name(x):
            return type(x).__name__

        ########

        ignore = set(ignore_cols or set())
        if dedupe_added:
            ignore.update({id_col, "created_at", "run_id", "old_uuid", "added"})
        else:
            ignore.update({id_col, "created_at", "run_id", "old_uuid"})

        if sort_key is None:
            sort_key = lambda r: r.get("created_at") or ""

        rows = self.selectAll(table_name)
        rows.sort(key=sort_key, reverse=True if sort_reverse else False)

        seen: dict[tuple, Any] = {}
        promote_added_ids: list[Any] = []

        for row in rows:
            key = tuple(sorted((k, repr(v)) for k, v in row.items() if k not in ignore))
            row_id = row.get(id_col)

            if key not in seen:
                seen[key] = row_id
            else:
                keeper_id = seen[key]
                if row.get("added") is True:
                    promote_added_ids.append(keeper_id)

                self.delete_these.append(row_id)

        # if promote_added_ids:
        #     promote_added_ids = list(dict.fromkeys([x for x in promote_added_ids if x]))
        #     for i in range(0, len(promote_added_ids), 200):
        #         chunk = promote_added_ids[i : i + 200]
        #         self.supabase.table(table_name).update({"added": True}).in_(id_col, chunk).execute()

        if promote_added_ids:
            promote_added_ids = list(dict.fromkeys([x for x in promote_added_ids if x]))
            for i in range(0, len(promote_added_ids), 200):
                chunk = promote_added_ids[i : i + 200]
                if not chunk:
                    print(f"[dedupeTable] Empty chunk at i={i}, skipping", flush=True)
                    continue

                # ===== DEBUG PRINTS =====
                print("\n[dedupeTable] About to promote added=True", flush=True)
                print(f"[dedupeTable] table_name={table_name} id_col={id_col}", flush=True)
                print(f"[dedupeTable] chunk_index_start={i} chunk_size={len(chunk)}", flush=True)

                # Quick validity checks
                none_count = sum(x is None for x in chunk)
                empty_str_count = sum((isinstance(x, str) and x.strip() == "") for x in chunk)
                print(f"[dedupeTable] none_count={none_count} empty_str_count={empty_str_count}", flush=True)

                # Type distribution (super useful for CI-only weirdness)
                type_counts = {}
                for x in chunk:
                    t = _type_name(x)
                    type_counts[t] = type_counts.get(t, 0) + 1
                print(f"[dedupeTable] type_counts={type_counts}", flush=True)

                # Preview IDs (masked so logs are safe)
                preview = chunk[:3] + (["..."] if len(chunk) > 6 else []) + chunk[-3:]
                preview_masked = [_mask_id(x) if x != "..." else "..." for x in preview]
                print(f"[dedupeTable] chunk_preview={preview_masked}", flush=True)

                # Full query description (no secrets)
                print(f"[dedupeTable] Running: update({{'added': True}}).in_({id_col}, <{len(chunk)} ids>)", flush=True)

                # ===== ACTUAL CALL =====
                try:
                    resp = self.supabase.table(table_name).update({"added": True}).in_(id_col, chunk).execute()
                    # resp shape varies by client version; print something resilient:
                    data_len = len(getattr(resp, "data", []) or [])
                    print(f"[dedupeTable] Update succeeded. returned_rows={data_len}", flush=True)
                except Exception as e:
                    print(f"[dedupeTable] Update FAILED: {e!r}", flush=True)
                    # Print a little more context without dumping everything
                    print(f"[dedupeTable] First_id={_mask_id(chunk[0])} Last_id={_mask_id(chunk[-1])}", flush=True)
                    raise

        #######

        if self.delete_these:
            self.deleteTheseRows(table_name, primary_key=id_col, refresh=refresh)
