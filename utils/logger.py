import logging, os, sys, traceback, pathlib, time, threading, re

logger = logging.getLogger("sel")


def dump_artifacts(driver, prefix: str = "fail", note: str | None = None) -> tuple[str, str]:
    """
    Saves a screenshot and page_source into utils/logger_artifacts/.
    Returns (png_path, html_path).
    """
    artifact_dir = pathlib.Path("utils/logger_artifacts")

    ts = time.strftime("%Y%m%d-%H%M%S")
    thread_name = threading.current_thread().name.replace(" ", "_")
    safe_prefix = prefix.replace(" ", "_")
    base = artifact_dir / f"{safe_prefix}-{thread_name}-{ts}"
    if note:
        base = str(base) + f"-{note}"
    else:
        base = str(base)

    png_path = f"{base}.png"
    html_path = f"{base}.html"

    try:
        if getattr(driver, "save_screenshot", None):
            driver.save_screenshot(png_path)
    except Exception as e:
        logger.warning("Failed to save screenshot: %s", e)

    try:
        src = getattr(driver, "page_source", "") or ""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(src)
    except Exception as e:
        logger.warning("Failed to save page_source: %s", e)

    return png_path, html_path


def setup_logging(level: str | int = None) -> None:
    if level is None:
        level = os.getenv("LOG_LEVEL", "DEBUG")
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logger.setLevel(level)

    artifact_dir = pathlib.Path("utils/logger_artifacts")
    # Clean up old artifacts on each run
    if artifact_dir.exists():
        for f in artifact_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
    artifact_dir.mkdir(parents=True, exist_ok=True)


def artifactPrinting(obj=None, *, driver=None, prefix=None, url=None, note: str | None = None):
    try:
        name = prefix or (getattr(obj, "CINEMA_NAME", None) or (obj.__class__.__name__ if obj else "Unknown"))
    except Exception:
        name = "Unknown"

    drv = driver or (getattr(obj, "driver", None) if obj is not None else None)
    if url is None:
        try:
            url = getattr(drv, "current_url", "?")
        except Exception:
            url = "?"

    exc_type, exc_value, tb = sys.exc_info()
    frames = traceback.extract_tb(tb)

    filtered = []
    for f in frames:
        path = f.filename.replace("\\", "/")
        if any(s in path for s in ("/site-packages/", "/dist-packages/", "/lib/python", "/.venv/", "/venv/", "/pyenv/", "/conda/", "/selenium/", "selenium")):
            continue
        if os.path.basename(path) in {"webdriver.py", "errorhandler.py", "remote_connection.py", "service.py"}:
            continue
        filtered.append(f)

    tail = (filtered or frames)[-5:]
    call_chain = " > ".join(f"{os.path.basename(f.filename)}:{f.lineno}" for f in tail)

    exc_type_name = exc_type.__name__ if exc_type else "Exception"
    exc_msg = str(exc_value) if exc_value else ""
    exc_msg = "\n".join(ln for ln in (str(exc_value) if exc_value else "").splitlines() if not any(b in ln.lower() for b in ("stacktrace", "documentation", "<unknown>", "chromedriver", "libsystem_pthread.dylib")))

    match = re.search(r'"selector":\s*"([^"]+)"', exc_msg)
    selector = match.group(1) if match else None

    logger.error(
        "\n".join(
            [
                "Error:",
                "\n\n",
                "---------------------------------------------------------------------------------------------",
                "                                                                                             ",
                "                                            ERROR                                            ",
                "                                                                                             ",
                f"                                       {name}                                ",
                "                                                                                             ",
                "---------------------------------------------------------------------------------------------",
                f"URL:       {url}",
                f"Exception: {exc_type_name} - {exc_msg}",
                f"Location:  {call_chain}",
                *([f"Selector:  {selector}"] if selector else []),
            ]
        )
    )

    try:
        png, html = dump_artifacts(drv, prefix=name, note=note)
        print(f"  Screenshot: {png}\n  Html:       {html}", flush=True)
        return png, html
    except Exception as capture_err:
        print(f"    Failed to dump artifacts: {capture_err}", flush=True)
        return None, None
