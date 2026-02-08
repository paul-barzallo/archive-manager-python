#!/usr/bin/env python3
"""Centralized message access for UI components.

Call ``I18nMessages.configure(i18n_settings)`` at application startup
before using any message resolution methods.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar

from archive_manager.infrastructure.config import (
    DEFAULT_LANGUAGE,
    SERVICES,
    I18nSettings,
)
from archive_manager.infrastructure.i18n.loaders import I18nMessageLoader

logger = logging.getLogger(__name__)


@dataclass
class I18nMessage:
    """Resolved i18n message with optional HTTP status."""

    file_path: str
    code: str
    _message: str | None = None
    _http_status: str | None = None

    @property
    def message(self) -> str:
        """Return the message text, or ``[CODE]`` if unresolved."""
        return self._message if self._message is not None else f"[{self.code}]"

    @property
    def http_status(self) -> int:
        """Return the HTTP status code, or 0 if not set."""
        if self._http_status is None:
            return 0
        try:
            return int(self._http_status)
        except (TypeError, ValueError):
            return 0

    def formatted_message(self, **kwargs: Any) -> str:
        """Return the message formatted with the given keyword arguments."""
        if kwargs and self._message:
            try:
                return self._message.format(**kwargs)
            except (
                KeyError,
                ValueError,
                IndexError,
                AttributeError,
                TypeError,
            ) as e:
                logger.warning(
                    "Format error for message code %s in file %s with args %s: %s",
                    self.code,
                    self.file_path,
                    kwargs,
                    e,
                )
        return self.message

    def __str__(self) -> str:
        """String representation of the message."""
        return self.message


class I18nMessages:
    """Resolves i18n message codes from JSON files.

    Uses a fallback chain:
    1. service-specific file in the requested language
    2. global file in the requested language
    3. service-specific file in the default language
    4. global file in the default language
    """

    _SERVICE: ClassVar[str] = ""
    _i18n: ClassVar[I18nSettings | None] = None
    __loader: ClassVar[I18nMessageLoader] = I18nMessageLoader()
    __cache: ClassVar[dict[tuple[Path, str], I18nMessage]] = {}
    __file_locks: ClassVar[dict[Path, Lock]] = {}
    __lock: ClassVar[Lock] = Lock()

    @classmethod
    def configure(cls, i18n_settings: I18nSettings) -> None:
        """Inject i18n settings. Must be called before any message resolution.

        Args:
            i18n_settings: The I18nSettings instance to use.
        """
        cls._i18n = i18n_settings

    @classmethod
    def _get_i18n(cls) -> I18nSettings:
        """Return the configured i18n settings or raise if not set."""
        if cls._i18n is None:
            msg = "I18nMessages not configured. Call configure(i18n_settings) first."
            raise RuntimeError(msg)
        return cls._i18n

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all resolved-message caches."""
        with cls.__lock:
            cls.__cache.clear()
            cls.__file_locks.clear()
            cls.__loader.clear_cache()

    @classmethod
    def codes(cls) -> list[str]:
        """Return sorted list of cached message codes."""
        codes = set()
        with cls.__lock:
            for key in cls.__cache:
                codes.add(key[1])
        return sorted(codes)

    @classmethod
    def _find_message(
        cls, language: str, subdir: str, filename: str, code: str
    ) -> I18nMessage:
        """Resolve a message code through the fallback chain."""
        i18n = cls._get_i18n()
        file_path = i18n.get_file_path(
            language, cls._SERVICE, subdir, filename=filename
        ).resolve()
        with cls.__lock:
            lock = cls.__file_locks.get(file_path)
            if lock is None:
                cls.__file_locks[file_path] = Lock()
                lock = cls.__file_locks[file_path]

        with lock:
            if (file_path, code) in cls.__cache:
                return cls.__cache[(file_path, code)]

            file_path_global = i18n.get_file_path(
                language, None, subdir, filename=filename
            ).resolve()
            if (file_path_global, code) in cls.__cache:
                return cls.__cache[(file_path_global, code)]

            # Fallback chain: service → global → default-service → default-global
            candidates: list[Path] = [file_path]
            if cls._SERVICE:
                candidates.append(file_path_global)
            if language != DEFAULT_LANGUAGE:
                candidates.append(
                    i18n.get_file_path(
                        DEFAULT_LANGUAGE, cls._SERVICE, subdir, filename=filename
                    )
                )
                if cls._SERVICE:
                    candidates.append(
                        i18n.get_file_path(
                            DEFAULT_LANGUAGE, None, subdir, filename=filename
                        )
                    )

            for candidate in candidates:
                data = cls.__loader.get_i18nmessage(candidate, code=code)
                if data is not None:
                    i18nmsg = I18nMessage(
                        str(candidate),
                        code,
                        data.get("message"),
                        data.get("http_status"),
                    )
                    cls.__cache[(file_path, code)] = i18nmsg
                    return i18nmsg

        return I18nMessage(str(file_path), code)

    # --- Public convenience methods ---

    @classmethod
    def error(cls, language: str, code: str) -> I18nMessage:
        """Resolve an error message."""
        return cls._find_message(language, "output", "error.json", code)

    @classmethod
    def warning(cls, language: str, code: str) -> I18nMessage:
        """Resolve a warning message."""
        return cls._find_message(language, "output", "warning.json", code)

    @classmethod
    def success(cls, language: str, code: str) -> I18nMessage:
        """Resolve a success message."""
        return cls._find_message(language, "output", "success.json", code)

    @classmethod
    def prompt(cls, language: str, code: str, **kwargs: Any) -> str:
        """Resolve and format a prompt message."""
        data = cls._find_message(language, "visual", "prompts.json", code)
        return data.formatted_message(**kwargs)

    @classmethod
    def confirm(cls, language: str, code: str, **kwargs: Any) -> str:
        """Resolve and format a confirmation message."""
        data = cls._find_message(language, "visual", "confirm.json", code)
        return data.formatted_message(**kwargs)

    @classmethod
    def info(cls, language: str, code: str, **kwargs: Any) -> str:
        """Resolve and format an info message."""
        data = cls._find_message(language, "visual", "info.json", code)
        return data.formatted_message(**kwargs)

    @classmethod
    def field(cls, language: str, code: str, **kwargs: Any) -> str:
        """Resolve and format a field label."""
        data = cls._find_message(language, "visual", "fields.json", code)
        return data.formatted_message(**kwargs)


class ContactI18nMessages(I18nMessages):
    """Messages scoped to the contact service."""

    _SERVICE: ClassVar[str] = SERVICES.CONTACT
