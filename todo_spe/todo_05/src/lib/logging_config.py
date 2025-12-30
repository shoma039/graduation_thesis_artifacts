import logging
import os
from typing import Optional


DEFAULT_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


def configure_logging(level: Optional[int] = None, fmt: Optional[str] = None, logfile: Optional[str] = None) -> None:
    """Configure root logger with StreamHandler and optional FileHandler.

    - `level`: logging level (int). If None, read from `LOG_LEVEL` env var or default to INFO.
    - `fmt`: format string for log messages.
    - `logfile`: optional path to write logs to a file.

    Safe to call multiple times.
    """
    if level is None:
        env_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, env_level, logging.INFO)

    fmt = fmt or DEFAULT_FORMAT
    root = logging.getLogger()
    # remove existing handlers to avoid duplicates
    for h in list(root.handlers):
        root.removeHandler(h)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(stream_handler)

    if logfile:
        try:
            fh = logging.FileHandler(logfile)
            fh.setFormatter(logging.Formatter(fmt))
            root.addHandler(fh)
        except Exception:
            # If file handler cannot be created, fall back silently to stream only
            pass

    root.setLevel(level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger configured with the module's settings.

    Call `configure_logging()` early in application startup.
    """
    return logging.getLogger(name)
