import logging, os, sys, traceback, pathlib, time, threading, re, signal

ARTIFACT_ROOT = pathlib.Path("backend/utils/log/logger_artifacts")
logger = logging.getLogger("sel")
SUPPRESS_ERRORS = False


def setup_logging() -> None:
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


def artifactPrinting(obj, run_id):
    if SUPPRESS_ERRORS:
        return

    name = obj.__class__.__name__ if obj else "Unknown"
    drv = getattr(obj, "driver", None) if obj is not None else None

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
    exception_msg = cleaned_msg if exc_type_name == "Exception" else f"{exc_type_name} - {cleaned_msg}"

    match = re.search(r'"selector":\s*"([^"]+)"', cleaned_msg)
    selector = match.group(1) if match else None

    safe_prefix = (name or "fail").replace(" ", "_")
    thread_name = threading.current_thread().name.replace(" ", "_")
    ts = time.strftime("%Y%m%d-%H%M%S")

    artifact_dir = ARTIFACT_ROOT / str(run_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    base = artifact_dir / f"{safe_prefix}-{thread_name}-{ts}"
    png_path, txt_path = f"{base}.png", f"{base}.txt"
    screenshot_written = None

    try:
        (artifact_dir / ".job_ok").write_text("false", encoding="utf-8")
    except Exception:
        pass

    csv_written = getattr(obj, "_last_csv_artifact", None) if obj is not None else None
    if csv_written and not os.path.exists(csv_written):
        csv_written = None

    if drv:
        try:
            drv.save_screenshot(png_path)
            screenshot_written = png_path
        except Exception:
            pass

    try:
        lines = ["- - -", "ERROR", "- - -", f"Name: {name or ''}", f"URL: {url or ''}", f"Exception: {exception_msg or ''}", f"Call Chain: {call_chain or ''}", f"Selector: {selector or ''}", f"Screenshot: {screenshot_written or ''}", f"CSV: {csv_written or ''}"]
    try:
        lines = ["- - -", "ERROR", "- - -", f"Name: {name or ''}", f"URL: {url or ''}", f"Exception: {exception_msg or ''}", f"Call Chain: {call_chain or ''}", f"Selector: {selector or ''}", f"Screenshot: {screenshot_written or ''}", f"CSV: {csv_written or ''}"]
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass
