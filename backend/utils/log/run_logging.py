from supabase import create_client
from typing import Any, Callable
import os, time

CURRENT_RUN_ID: int | None = None
RUN_LOCK_SLEEP_SECONDS = 60
RUN_LOCK_MAX_MINUTES = 10


def allocate_run_id() -> int:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

    if os.environ.get("JJ_INTEL_MAC_WEEKLY_RUN") == "true":
        run_from = "JJ_INTEL_MAC_WEEKLY_RUN"
    elif os.environ.get("GITHUB_ACTIONS") == "true":
        run_from = "GITHUB_ACTIONS"
    else:
        run_from = os.environ.get("RUNNER_MACHINE") or "unknown"

    for _ in range(RUN_LOCK_MAX_MINUTES):
        rows = sb.table("utilRunLogs").select("run_id").eq("running_now", True).limit(1).execute().data
        if not rows:
            break
        time.sleep(RUN_LOCK_SLEEP_SECONDS)
    else:
        raise RuntimeError("run_id cannot be allocated - already in use in different runner")

    rows = sb.table("utilRunLogs").select("run_id").order("run_id", desc=True).limit(1).execute().data
    new_id = int(rows[0]["run_id"]) + 1
    sb.table("utilRunLogs").insert({"run_id": new_id, "running_now": True, "run_from": run_from}).execute()

    global CURRENT_RUN_ID
    CURRENT_RUN_ID = new_id
    return new_id


class RunLogSession:
    def __init__(self) -> None:
        self.run_id: int | None = None
        self._start_time: float = 0.0
        self._selected_runners: list[dict[str, Any]] = []
        self._successful: bool = True

    def __enter__(self) -> "RunLogSession":
        self.run_id = allocate_run_id()
        self._start_time = time.time()
        self._selected_runners = []
        self._successful = True
        return self

    def set_successful(self, ok: bool) -> None:
        self._successful = self._successful and bool(ok)

    def set_plan(self, plan: list[tuple]) -> None:
        out: list[dict[str, Any]] = []

        for entry in plan or []:
            if not isinstance(entry, tuple):
                continue
            if len(entry) == 2:
                kind, key = entry
                out.append({"kind": str(kind), "key": str(key)})
                continue
            if len(entry) == 3:
                kind, key, classes_override = entry
                class_names: list[str] = []
                if classes_override:
                    try:
                        class_names = [c.__name__ for c in classes_override]
                    except Exception:
                        class_names = []
                out.append({"kind": str(kind), "key": str(key), "classes_override": class_names})
                continue
            out.append({"raw_entry": repr(entry)})

        self._selected_runners = out

    def run_groups(self, plan: list[tuple], *, run_group_fn: Callable[..., bool]) -> bool:
        self.set_plan(plan)

        overall_ok = True
        for entry in plan or []:
            if len(entry) == 2:
                kind, key = entry
                ok = bool(run_group_fn(kind, key, self.run_id))
            else:
                kind, key, classes_override = entry
                ok = bool(run_group_fn(kind, key, self.run_id, classes_override=classes_override))

            overall_ok = overall_ok and ok

        self.set_successful(overall_ok)
        return overall_ok

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            self._successful = False

        if self.run_id is not None:
            total_time = time.time() - self._start_time
            try:
                sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
                sb.table("utilRunLogs").update({"selected_runners": self._selected_runners, "successful": bool(self._successful), "total_time": float(total_time), "running_now": False}).eq("run_id", int(self.run_id)).execute()
            except BaseException:
                pass

        return False
