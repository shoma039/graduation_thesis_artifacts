import logging


def setup_logging(debug: bool = False) -> None:
    """Configure module-level logging with a sensible default format.

    Call this at program startup (CLI entrypoint).
    """
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"

    # Basic config; libraries can use logging.getLogger(__name__)
    logging.basicConfig(level=level, format=fmt)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
