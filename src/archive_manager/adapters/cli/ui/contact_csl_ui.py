#!/usr/bin/env python3
"""Console UI for contact management.

This module provides the contact-specific UI with menus, tables,
and detailed contact views using Rich library formatting.
"""

from __future__ import annotations

from collections.abc import Sequence

from archive_manager.adapters.cli.ui.csl_ui import CslUI
from archive_manager.application.dto import ContactDTO
from archive_manager.infrastructure.i18n import (
    ContactI18nMenus,
    ContactI18nMessages,
    ContactI18nTables,
)


class ContactCslUI(CslUI):
    """Console UI for contact with menus, tables, and detail views.

    Extends CslUI with contact-specific functionality.
    Language is passed as parameter from AppContext to each method.
    Menus and tables loaded from i18n are safe to mutate per call because
    i18n resolvers return defensive copies of cached objects.
    """

    _I18N = ContactI18nMessages

    def show_contact_list_menu(self, language: str) -> str | None:
        """Display the main contact list menu.

        Args:
            language: Language code for i18n.

        Returns:
            Selected option ID or `None` if cancelled.
        """
        return self._show_menu(ContactI18nMenus.contact_list_menu(language))

    def show_contact_menu(self, language: str) -> str | None:
        """Display the single contact action menu.

        Args:
            language: Language code for i18n.

        Returns:
            Selected option ID or `None` if cancelled.
        """
        return self._show_menu(ContactI18nMenus.contact_menu(language))

    def show_find_contact_menu(self, language: str) -> str | None:
        """Display the find contact menu.

        Args:
            language: Language code for i18n.

        Returns:
            Selected option ID or `None` if cancelled.
        """
        return self._show_menu(ContactI18nMenus.find_contact_menu(language))

    def show_select_contact_menu(
        self, language: str, contacts: Sequence[ContactDTO]
    ) -> str:
        """Display a menu to select from a Sequence of contacts.

        Args:
            language: Language code for i18n.
            contacts: Sequence of contacts to display as options.

        Returns:
            Selected contact index as string, or 'return' option ID.
        """
        menu = ContactI18nMenus.select_contact_menu(language)
        option_return = menu.options[-1]
        menu.clear_options()
        for i, contact in enumerate(contacts):
            detail = "< "
            detail += " | ".join(
                f"{item['text']}: {item['value']}"
                for item in self._get_contact_fields(language, contact)
            )
            detail += " >"
            menu.add_option(str(i), detail)
        menu.add_option(option_return.id, option_return.text)
        return self._show_menu(menu)

    def show_contacts_table(
        self,
        language: str,
        contacts: Sequence[ContactDTO],
        total: int | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> None:
        """Display a table of contacts.

        Args:
            language: Language code for i18n.
            contacts: Sequence of contacts to display.
            total: Total number of available contacts across all pages.
            limit: Page size used for pagination metadata.
            offset: Zero-based index of the first element shown.
        """
        footer_context = self._build_contacts_footer_context(
            shown=len(contacts),
            total=total,
            limit=limit,
            offset=offset,
        )
        self._show_table(
            ContactI18nTables.contact_table(language),
            contacts,
            **footer_context,
        )

    @staticmethod
    def _build_contacts_footer_context(
        shown: int,
        total: int | None,
        limit: int | None,
        offset: int,
    ) -> dict[str, int]:
        """Build normalized footer values for paginated contact tables.

        Supports both full-list rendering (when ``total`` is not provided)
        and true paginated rendering (when ``total``/``limit``/``offset`` are
        provided by the controller).
        """
        total_value = shown if total is None else max(0, total)
        safe_limit = max(1, shown if limit is None else limit)
        safe_offset = max(0, offset)

        if shown == 0:
            start = 0
            end = 0
        else:
            start = safe_offset + 1
            end = safe_offset + shown

        if total_value == 0:
            page = 0
            pages = 0
        else:
            pages = (total_value + safe_limit - 1) // safe_limit
            page = min((safe_offset // safe_limit) + 1, pages)

        return {
            "shown": shown,
            "total": total_value,
            "start": start,
            "end": end,
            "page": page,
            "pages": pages,
        }

    def show_contact_list_pagination_menu(
        self,
        language: str,
        has_previous: bool,
        has_next: bool,
    ) -> str:
        """Display pagination actions for contact list navigation.

        Args:
            language: Language code for i18n.
            has_previous: Whether previous page is available.
            has_next: Whether next page is available.

        Returns:
            Selected option ID.
        """
        menu = ContactI18nMenus.contact_pagination_menu(language)
        options = {option.id: option.text for option in menu.options}
        menu.clear_options()

        if has_previous and "previous" in options:
            menu.add_option("previous", options["previous"])
        if has_next and "next" in options:
            menu.add_option("next", options["next"])

        # Return must always be available.
        menu.add_option("return", options.get("return", "Return"))
        return self._show_menu(menu, clear_screen=False)

    def show_contact_detail(self, language: str, contact: ContactDTO) -> None:
        """Display detailed information for a single contact.

        Args:
            language: Language code for i18n.
            contact: Contact to display.
        """
        title = self._I18N.field(language, "TITLE_CONTACT_DETAILS")
        self._show_details(
            title,
            self._get_contact_fields(language, contact),
        )

    def _get_contact_fields(
        self, language: str, contact: ContactDTO
    ) -> Sequence[dict[str, str]]:
        """Convert contact to Sequence of field dicts for display.

        Args:
            language: Language code for i18n.
            contact: Contact to convert.

        Returns:
            Sequence of dicts with 'text' and 'value' keys.
        """
        return [
            {
                "text": self._I18N.field(language, field["code"]),
                "value": field["value"],
            }
            for field in contact.as_fields()
        ]
