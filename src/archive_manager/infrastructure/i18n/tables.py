#!/usr/bin/env python3
"""Table configuration and loader for UI components.

Call ``I18nTables.configure(i18n_settings)`` at application startup.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar

from rich import box
from rich.table import Table

from archive_manager.core.errors import AppException
from archive_manager.infrastructure.config import SERVICES, I18nSettings
from archive_manager.infrastructure.i18n.loaders import I18nTablesLoader


@dataclass
class I18nTable:
    """Table layout definition with title, headers, and optional footer."""

    title: str
    headers: dict[str, str]
    footer: str = ""

    def build_table(self, data: list[dict[str, Any]], **kwargs: Any) -> Table:
        """Build a Rich Table from data rows."""
        table = Table(
            title=self.title or None,
            box=box.ROUNDED,
            border_style="cyan1",
            show_header=True,
            header_style="bold cyan1",
            show_lines=True,
            padding=(0, 1),
        )
        table.add_column("#", style="bold cyan1")
        for header in self.headers.values():
            table.add_column(header)
        for i, element in enumerate(data):
            row_values = [str(i + 1)]
            for key in self.headers:
                value = element.get(key, "")
                row_values.append(str(value))
            table.add_row(*row_values)
        if kwargs and self.footer:
            table.caption = self.footer.format(**kwargs)
            table.caption_style = "dim"
        return table


class I18nTables:
    """Resolves table definitions from JSON files.

    Cached table instances are never exposed directly; callers receive a
    defensive deep copy to avoid shared-state mutations.
    """

    _SERVICE: ClassVar[str] = ""
    _i18n: ClassVar[I18nSettings | None] = None
    __loader: ClassVar[I18nTablesLoader] = I18nTablesLoader()
    __cache: ClassVar[dict[tuple[Path, str], I18nTable]] = {}
    __file_locks: ClassVar[dict[Path, Lock]] = {}
    __lock: ClassVar[Lock] = Lock()

    @classmethod
    def configure(cls, i18n_settings: I18nSettings) -> None:
        """Inject i18n settings. Must be called at startup."""
        cls._i18n = i18n_settings

    @classmethod
    def _get_i18n(cls) -> I18nSettings:
        """Return the configured i18n settings or raise if not set."""
        if cls._i18n is None:
            msg = "I18nTables not configured. Call configure(i18n_settings) first."
            raise RuntimeError(msg)
        return cls._i18n

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached tables and file locks."""
        with cls.__lock:
            cls.__cache.clear()
            cls.__file_locks.clear()
            cls.__loader.clear_cache()

    @classmethod
    def names(cls) -> list[str]:
        """Return sorted list of cached table names."""
        names = set()
        with cls.__lock:
            for key in cls.__cache:
                names.add(key[1])
        return sorted(names)

    @classmethod
    def _load_table(cls, language: str, table_name: str) -> I18nTable:
        """Load and cache a table definition from its JSON file.

        Returns a deep copy so callers cannot mutate the shared cache.
        """
        i18n = cls._get_i18n()
        file_path = i18n.get_file_path(
            language, cls._SERVICE, filename="tables.json"
        ).resolve()
        with cls.__lock:
            lock = cls.__file_locks.get(file_path)
            if lock is None:
                cls.__file_locks[file_path] = Lock()
                lock = cls.__file_locks[file_path]
        with lock:
            if (file_path, table_name) in cls.__cache:
                return deepcopy(cls.__cache[(file_path, table_name)])
            data = cls.__loader.get_i18ntable(file_path, table_name)
            if data is not None:
                i18ntable = I18nTable(
                    title=data.get("title", ""),
                    headers=data.get("headers", {}),
                    footer=data.get("footer", ""),
                )
                cls.__cache[(file_path, table_name)] = i18ntable
                return deepcopy(i18ntable)
        raise AppException(
            code="TABLE_NOT_FOUND",
            origin="I18nTables._load_table",
            missing_table=table_name,
            language=language,
        )


class ContactI18nTables(I18nTables):
    """Table definitions scoped to the contact service."""

    _SERVICE: ClassVar[str] = SERVICES.CONTACT

    @classmethod
    def contact_table(cls, language: str) -> I18nTable:
        """Return the contact table layout for the given language."""
        return cls._load_table(language, "contact_table")
