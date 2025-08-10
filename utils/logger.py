import logging, os, sys

logger = logging.getLogger("sel")


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
