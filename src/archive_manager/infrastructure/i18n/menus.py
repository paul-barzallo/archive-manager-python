#!/usr/bin/env python3
"""Menu configuration and loader for UI components.

Call ``I18nMenus.configure(i18n_settings)`` at application startup.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import ClassVar

from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle

from archive_manager.core.errors import AppException
from archive_manager.infrastructure.config import SERVICES, I18nSettings
from archive_manager.infrastructure.i18n.loaders import I18nMenusLoader


@dataclass
class I18nMenuOption:
    """Single menu option with id and display text."""

    id: str
    text: str


@dataclass
class I18nMenu:
    """Menu with a title and a list of options."""

    title: str
    options: list[I18nMenuOption]

    @property
    def num_options(self) -> int:
        """Return the number of options in the menu."""
        return len(self.options)

    def get_option_id(self, indice: int) -> str | None:
        """Return the option ID at the given 1-based index, or ``None``."""
        if 1 <= indice <= self.num_options:
            return self.options[indice - 1].id
        return None

    def add_option(self, id: str, text: str) -> None:
        """Append a new option to the menu."""
        self.options.append(I18nMenuOption(id=id, text=text))

    def clear_options(self) -> None:
        """Remove all options from the menu."""
        self.options.clear()

    def prompt_choice(self, style: InquirerPyStyle) -> str:
        """Display the menu interactively and return the chosen option ID."""
        choices: list[dict[str, str] | Separator] = [
            Separator(self.title),
            Separator(""),
        ]
        choices.extend(
            {"name": f"{i + 1}. {option.text}", "value": option.id}
            for i, option in enumerate(self.options)
        )
        result: str = ListPrompt(
            message="",
            choices=choices,
            qmark="",
            amark="",
            pointer=">",
            instruction="",
            long_instruction="",
            style=style,
            show_cursor=False,
            cycle=True,
        ).execute()
        return result


class I18nMenus:
    """Resolves menu definitions from JSON files.

    Cached menu instances are never exposed directly; callers receive a
    defensive deep copy so runtime menu mutations stay request-local.
    """

    _SERVICE: ClassVar[str] = ""
    _i18n: ClassVar[I18nSettings | None] = None
    __loader: ClassVar[I18nMenusLoader] = I18nMenusLoader()
    __cache: ClassVar[dict[tuple[Path, str], I18nMenu]] = {}
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
            msg = "I18nMenus not configured. Call configure(i18n_settings) first."
            raise RuntimeError(msg)
        return cls._i18n

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached menus and file locks."""
        with cls.__lock:
            cls.__cache.clear()
            cls.__file_locks.clear()
            cls.__loader.clear_cache()

    @classmethod
    def names(cls) -> list[str]:
        """Return sorted list of cached menu names."""
        names: set[str] = set()
        with cls.__lock:
            for key in cls.__cache:
                names.add(key[1])
        return sorted(names)

    @classmethod
    def _load_menu(cls, language: str, menu_name: str) -> I18nMenu:
        """Load and cache a menu definition from its JSON file.

        Returns a deep copy so callers can safely mutate dynamic options.
        """
        i18n = cls._get_i18n()
        file_path = i18n.get_file_path(
            language, cls._SERVICE, filename="menus.json"
        ).resolve()
        with cls.__lock:
            lock = cls.__file_locks.get(file_path)
            if lock is None:
                cls.__file_locks[file_path] = Lock()
                lock = cls.__file_locks[file_path]
        with lock:
            if (file_path, menu_name) in cls.__cache:
                return deepcopy(cls.__cache[(file_path, menu_name)])
            data = cls.__loader.get_i18nmenu(file_path, menu_name)
            if data is not None:
                i18nmenu = I18nMenu(
                    title=data.get("title", ""),
                    options=[
                        I18nMenuOption(id=opt["id"], text=opt["text"])
                        for opt in data.get("options", [])
                    ],
                )
                cls.__cache[(file_path, menu_name)] = i18nmenu
                return deepcopy(i18nmenu)
        raise AppException(
            code="MENU_NOT_FOUND",
            origin="I18nMenus._load_menu",
            missing_menu=menu_name,
            language=language,
        )


class ContactI18nMenus(I18nMenus):
    """Menu definitions scoped to the contact service."""

    _SERVICE: ClassVar[str] = SERVICES.CONTACT

    @classmethod
    def contact_list_menu(cls, language: str) -> I18nMenu:
        """Return the contact list menu for the given language."""
        return cls._load_menu(language, "contact_list_menu")

    @classmethod
    def find_contact_menu(cls, language: str) -> I18nMenu:
        """Return the find-contact menu for the given language."""
        return cls._load_menu(language, "find_contact_menu")

    @classmethod
    def select_contact_menu(cls, language: str) -> I18nMenu:
        """Return the select-contact menu for the given language."""
        return cls._load_menu(language, "select_contact_menu")

    @classmethod
    def contact_menu(cls, language: str) -> I18nMenu:
        """Return the single-contact action menu for the given language."""
        return cls._load_menu(language, "contact_menu")

    @classmethod
    def contact_pagination_menu(cls, language: str) -> I18nMenu:
        """Return the contact-list pagination menu for the given language."""
        return cls._load_menu(language, "contact_pagination_menu")
