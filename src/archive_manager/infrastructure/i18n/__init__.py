#!/usr/bin/env python3
"""Internationalization (i18n) infrastructure — file loading and caching.

All i18n classes must be configured via ``configure(i18n_settings)``
before use. This replaces the previous global ``get_settings()`` singleton.
"""

from archive_manager.infrastructure.i18n.loaders import (
    I18nMenusLoader,
    I18nMessageLoader,
    I18nTablesLoader,
)
from archive_manager.infrastructure.i18n.menus import (
    ContactI18nMenus,
    I18nMenu,
    I18nMenuOption,
    I18nMenus,
)
from archive_manager.infrastructure.i18n.messages import (
    ContactI18nMessages,
    I18nMessage,
    I18nMessages,
)
from archive_manager.infrastructure.i18n.tables import (
    ContactI18nTables,
    I18nTable,
    I18nTables,
)

__all__ = [
    "ContactI18nMenus",
    "ContactI18nMessages",
    "ContactI18nTables",
    "I18nMenu",
    "I18nMenuOption",
    "I18nMenus",
    "I18nMenusLoader",
    "I18nMessage",
    "I18nMessageLoader",
    "I18nMessages",
    "I18nTable",
    "I18nTables",
    "I18nTablesLoader",
]
