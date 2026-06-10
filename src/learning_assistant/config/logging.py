"""Structured logging configuration."""

import logging
import sys
from typing import Literal

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
_ALLOWED_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def setup_logging(level: LogLevel = "INFO") -> None:
    """Configure root logger with structured format.

    Idempotent — safe to call multiple times; reconfigures the root logger
    each time so the latest level/format wins.
    """
    upper = level.upper()
    if upper not in _ALLOWED_LEVELS:
        msg = f"log level must be one of {_ALLOWED_LEVELS}, got '{level}'"
        raise ValueError(msg)
    numeric_level = getattr(logging, upper)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicate output on re-init
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))
    root.addHandler(handler)
