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
        self, language: str, contacts: Sequence[ContactDTO]
    ) -> None:
        """Display a table of contacts.

        Args:
            language: Language code for i18n.
            contacts: Sequence of contacts to display.
        """
        self._show_table(ContactI18nTables.contact_table(language), contacts)

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
