import logging, os, sys, traceback, pathlib, time, threading, re, signal
from supabase import create_client
from typing import Any, Callable

logger = logging.getLogger("sel")
SUPPRESS_ERRORS = False
CURRENT_RUN_ID: int | None = None


RUN_LOCK_SLEEP_SECONDS = 60
RUN_LOCK_MAX_MINUTES = 20


def _compute_run_from() -> str:
    if os.environ.get("JJ_INTEL_MAC_WEEKLY_RUN") == "true":
        return "JJ_INTEL_MAC_WEEKLY_RUN"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "GITHUB_ACTIONS"
    return os.environ.get("RUNNER_MACHINE") or "unknown"


def allocate_run_id() -> int:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    run_from = _compute_run_from()

    for _minute in range(RUN_LOCK_MAX_MINUTES):
        rows = sb.table("utilRunLogs").select("run_id").eq("running_now", True).limit(1).execute().data or []
        if not rows:
            break
        time.sleep(RUN_LOCK_SLEEP_SECONDS)
    else:
        raise RuntimeError("run_id cannot be allocated - already in use in different runner")

    rows = sb.table("utilRunLogs").select("run_id").order("run_id", desc=True).limit(1).execute().data or []
    latest = int(rows[0].get("run_id")) if rows else 0
    new_id = latest + 1

    sb.table("utilRunLogs").insert({"run_id": new_id, "running_now": True, "run_from": run_from}).execute()

    global CURRENT_RUN_ID
    CURRENT_RUN_ID = new_id
    return new_id


def finalize_run_log(run_id: int, *, selected_runners: list[dict], successful: bool, total_time: float) -> None:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    sb.table("utilRunLogs").update({"selected_runners": selected_runners, "successful": bool(successful), "total_time": float(total_time), "running_now": False}).eq("run_id", int(run_id)).execute()


def _serialize_plan(plan: list[tuple]) -> list[dict[str, Any]]:
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
    return out


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

    def set_plan(self, plan: list[tuple]) -> None:
        self._selected_runners = _serialize_plan(plan)

    def set_successful(self, ok: bool) -> None:
        self._successful = self._successful and bool(ok)

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
                finalize_run_log(self.run_id, selected_runners=self._selected_runners, successful=self._successful, total_time=total_time)
            except BaseException:
                pass

        return False


def setup_logging() -> None:
    global SUPPRESS_ERRORS

    def _handler(sig, frame):
        global SUPPRESS_ERRORS
        SUPPRESS_ERRORS = True
        signal.default_int_handler(sig, frame)

    try:
        signal.signal(signal.SIGINT, _handler)
    except Exception:
        pass

    logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s", handlers=[logging.StreamHandler(sys.stdout)], force=True)
    logger.setLevel(logging.ERROR)

    artifact_dir = pathlib.Path("backend/utils/log/logger_artifacts")
    if artifact_dir.exists():  # Clean up old artifacts on each run
        for f in artifact_dir.glob("*"):
            try:
                f.unlink()
            except:
                pass
    artifact_dir.mkdir(parents=True, exist_ok=True)


def artifactPrinting(obj=None, *, driver=None, prefix=None, url=None, note: str | None = None):
    if SUPPRESS_ERRORS:
        return

    name = "Unknown"
    for attr in ["CINEMA_NAME", "MAIN_TABLE_NAME", "DUPLICATE_TABLE_NAME", "MOVING_TO_TABLE_NAME", "HELPER_TABLE_NAME"]:
        try:
            name = prefix or (getattr(obj, attr, None) or (obj.__class__.__name__ if obj else "Unknown"))
            break
        except Exception:
            pass

    drv = driver or (getattr(obj, "driver", None) if obj is not None else None)
    if url is None:
        try:
            url = getattr(drv, "current_url", "?") if drv else "?"
        except Exception:
            url = "?"

    exc_type, exc_value, tb = sys.exc_info()
    if tb is None or exc_type in (KeyboardInterrupt, SystemExit) or isinstance(exc_value, KeyboardInterrupt):
        return

    frames, filtered = traceback.extract_tb(tb), []
    for frame in frames:
        path = frame.filename.replace("\\", "/")
        if any(s in path for s in ("/site-packages/", "/dist-packages/", "/lib/python", "/.venv/", "/venv/", "/pyenv/", "/conda/", "/selenium/", "selenium")):
            continue
        if os.path.basename(path) in {"webdriver.py", "errorhandler.py", "remote_connection.py", "service.py"}:
            continue
        filtered.append(frame)

    tail = (filtered or frames)[-5:]
    call_chain = " > ".join(f"{os.path.basename(f.filename)}:{f.lineno}" for f in tail)

    exc_type_name = exc_type.__name__ if exc_type else "Exception"
    raw_msg = str(exc_value) if exc_value else ""
    cleaned_msg = "\n".join(ln for ln in raw_msg.splitlines() if not any(b in ln.lower() for b in ("stacktrace", "documentation", "<unknown>", "chromedriver", "libsystem_pthread.dylib")))
    exception_msg = f"{cleaned_msg}" if exc_type_name == "Exception" else f"{exc_type_name} - {cleaned_msg}"

    match = re.search(r'"selector":\s*"([^"]+)"', cleaned_msg)
    selector = match.group(1) if match else None

    artifact_dir = pathlib.Path("backend/utils/log/logger_artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%S")
    thread_name = threading.current_thread().name.replace(" ", "_")
    safe_prefix = (name or "fail").replace(" ", "_")

    base = artifact_dir / f"{safe_prefix}-{thread_name}-{ts}"
    if note:
        base = pathlib.Path(str(base) + f"-{note}")

    png_path, html_path, txt_path = f"{base}.png", f"{base}.html", f"{base}.txt"
    screenshot_written, html_written = None, None

    csv_written = getattr(obj, "_last_csv_artifact", None) if obj is not None else None
    if csv_written and not os.path.exists(csv_written) or not csv_written:
        csv_written = None

    try:
        if drv:
            try:
                drv.save_screenshot(png_path)
                screenshot_written = png_path
            except Exception:
                screenshot_written = None

            try:
                src = getattr(drv, "page_source", "") or ""
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(src)
                html_written = html_path
            except Exception:
                html_written = None
    except Exception:
        screenshot_written, html_written = None, None

    try:
        lines = ["- - -", "ERROR", "- - -", f"Name: {name or ''}", f"URL: {url or ''}", f"Exception: {exception_msg or ''}", f"Call Chain: {call_chain or ''}", f"Selector: {selector or ''}", f"Screenshot: {screenshot_written or ''}", f"HTML: {html_written or ''}", f"CSV: {csv_written or ''}"]
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass
