#!/usr/bin/env python3
"""Base loaders for i18n JSON files with caching.

These loaders return raw dictionaries from the shared JSON cache.
Callers that need mutation-safe objects should use typed resolvers
(``I18nMenus`` / ``I18nTables``), which provide defensive copies.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar, cast

logger = logging.getLogger(__name__)


class _I18nBaseLoader:
    """Base loader for i18n JSON files. Caches JSON data by file path."""

    __cache: ClassVar[dict[Path, dict[str, Any]]] = {}
    __file_locks: ClassVar[dict[Path, Lock]] = {}
    __cls_locks: ClassVar[dict[type[_I18nBaseLoader], Lock]] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the file cache."""
        lock = cls.__cls_locks.get(cls)
        if lock is None:
            cls.__cls_locks[cls] = Lock()
            lock = cls.__cls_locks[cls]
        with lock:
            cls.__cache.clear()
            cls.__file_locks.clear()

    @classmethod
    def _load_data(cls, path: Path) -> dict[str, Any]:
        """Load and cache JSON data from the given file path."""
        cache_key = path.resolve()
        cls_lock = cls.__cls_locks.get(cls)
        if cls_lock is None:
            cls.__cls_locks[cls] = Lock()
            cls_lock = cls.__cls_locks[cls]
        with cls_lock:
            lock = cls.__file_locks.get(cache_key)
            if lock is None:
                cls.__file_locks[cache_key] = Lock()
                lock = cls.__file_locks[cache_key]
        with lock:
            if cache_key not in cls.__cache:
                try:
                    with path.resolve().open(encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            cls.__cache[cache_key] = data
                        else:
                            logger.warning(
                                "Unexpected data format in file: %s", cache_key
                            )
                            cls.__cache[cache_key] = {}
                except FileNotFoundError:
                    logger.info("File not found: %s", cache_key)
                    cls.__cache[cache_key] = {}
                except json.JSONDecodeError:
                    logger.exception("JSON decode error in file: %s", cache_key)
                    cls.__cache[cache_key] = {}
        return cls.__cache[cache_key]


class I18nMessageLoader(_I18nBaseLoader):
    """Loader for individual i18n message entries."""

    @classmethod
    def get_i18nmessage(cls, file_path: Path, code: str) -> dict[str, str] | None:
        """Load a message by code from a JSON file."""
        item = cls._load_data(file_path)
        if not item:
            logger.warning("No data loaded from file %s", file_path)
            return None
        message_data = item.get(code)
        if not message_data:
            logger.warning("Message code %s in file %s not found", code, file_path)
            return None
        if not isinstance(message_data, dict):
            logger.warning(
                "Message for code %s in file %s is not a dict %s",
                code,
                file_path,
                message_data,
            )
            return None
        return cast(dict[str, str], message_data)


class I18nMenusLoader(_I18nBaseLoader):
    """Loader for menu configuration entries.

    Returned dictionaries are cache-backed and should be treated as read-only.
    """

    @classmethod
    def get_i18nmenu(cls, file_path: Path, menu_name: str) -> dict[str, Any] | None:
        """Load a menu definition by name from a JSON file."""
        item = cls._load_data(file_path)
        if not item:
            logger.warning("No data loaded from file %s", file_path)
            return None
        menu_data = item.get(menu_name)
        if not menu_data:
            logger.warning("Menu name %s in file %s not found", menu_name, file_path)
            return None
        if not isinstance(menu_data, dict):
            logger.warning(
                "Menu for name %s in file %s is not a dict: %s",
                menu_name,
                file_path,
                menu_data,
            )
            return None
        return cast(dict[str, Any], menu_data)


class I18nTablesLoader(_I18nBaseLoader):
    """Loader for table configuration entries.

    Returned dictionaries are cache-backed and should be treated as read-only.
    """

    @classmethod
    def get_i18ntable(cls, file_path: Path, table_name: str) -> dict[str, Any] | None:
        """Load a table definition by name from a JSON file."""
        item = cls._load_data(file_path)
        if not item:
            logger.warning("No data loaded from file %s", file_path)
            return None
        table_data = item.get(table_name)
        if not table_data:
            logger.warning("Table name %s in file %s not found", table_name, file_path)
            return None
        if not isinstance(table_data, dict):
            logger.warning(
                "Table for name %s in file %s is not a dict: %s",
                table_name,
                file_path,
                table_data,
            )
            return None
        return cast(dict[str, Any], table_data)
