import logging, os, sys
import pathlib, time, threading

logger = logging.getLogger("sel")


def dump_artifacts(driver, prefix: str = "fail", note: str | None = None) -> tuple[str, str]:
    """
    Saves a screenshot and page_source into utils/logger_artifacts/.
    Returns (png_path, html_path).
    """
    artifact_dir = pathlib.Path("utils/logger_artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)

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
