#!/usr/bin/env python3
"""Logging configuration module.

Simple, centralized logging setup. One format, clear output.
Uses ``RotatingFileHandler`` for log rotation in production.

Usage:
    from archive_manager.infrastructure.config.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Something happened")
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Any, Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_configured = False

# Default rotation settings
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_BACKUP_COUNT = 5


def configure_logging(
    level: LogLevel = "INFO",
    log_dir: Path | None = None,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    debug: bool = False,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> None:
    """Configure the logging system with rotating file handlers.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Directory for log files. If None, only uses NullHandler.
        log_format: Format string for log messages.
        date_format: Format string for timestamps.
        debug: If True, forces DEBUG level.
        max_bytes: Maximum log file size before rotation.
        backup_count: Number of rotated log files to keep.
    """
    global _configured
    if _configured:
        return

    effective_level = "DEBUG" if debug else level

    handlers: dict[str, dict[str, str | int]] = {}
    root_handlers: list[str] = []

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)

        handlers["debug_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": str(log_dir / "debug.log"),
            "formatter": "standard",
            "encoding": "utf-8",
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        }
        handlers["info_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": str(log_dir / "info.log"),
            "formatter": "standard",
            "encoding": "utf-8",
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        }
        handlers["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": str(log_dir / "error.log"),
            "formatter": "standard",
            "encoding": "utf-8",
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        }
        root_handlers = ["debug_file", "info_file", "error_file"]

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": date_format,
            }
        },
        "handlers": handlers,
        "root": {
            "level": effective_level,
            "handlers": root_handlers,
        },
    }

    logging.config.dictConfig(config)
    _configured = True


def reset_logging() -> None:
    """Reset logging configuration. Useful for tests."""
    global _configured
    _configured = False
    root = logging.getLogger()
    root.handlers.clear()


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Standard logging.Logger instance.
    """
    return logging.getLogger(name)
