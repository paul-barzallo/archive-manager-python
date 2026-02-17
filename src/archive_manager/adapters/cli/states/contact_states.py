#!/usr/bin/env python3
"""Console state machine for contact management application.

Orchestrates user interaction via CslUI, menu navigation via Menus,
and business logic via ContactService. Handles domain-specific errors
and displays localized messages.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from archive_manager.adapters.cli.states.base_state import AppContext, BaseState
from archive_manager.adapters.cli.ui.contact_csl_ui import ContactCslUI
from archive_manager.application.dto import ContactDTO, ContactPageDTO
from archive_manager.infrastructure.config import PAGINATION

if TYPE_CHECKING:
    from archive_manager.application.services import ContactService

logger = logging.getLogger(__name__)

# Type alias for contact-specific context (string annotation for runtime)
ContactContext: TypeAlias = AppContext[ContactCslUI, "ContactService"]


# --- State Machines ---
class MainContactMenuState(BaseState):
    """Main menu state for contact management operations."""

    @BaseState.handle_errors
    def run(self, ctx: ContactContext) -> BaseState | None:
        """Execute main menu and handle user selection.

        Args:
            ctx: Application context with UI and service.

        Returns:
            Next state or `None` to exit.
        """
        ui = ctx.ui
        lang = ctx.session.language

        option_id = ui.show_contact_list_menu(lang)

        if option_id == "add":
            contact = ContactDTO()
            self._add_contact(ctx, contact)
            return self

        if option_id == "list":
            return _ListContactsState()

        if option_id == "find":
            return _FindMenuState()

        # Exit options
        if option_id in ("return", "exit", ""):
            return None

        # Unknown option: retry
        return self

    @BaseState.handle_errors
    def _add_contact(self, ctx: ContactContext, contact: ContactDTO) -> None:
        """Prompt for contact data, persist it, and show confirmation."""
        ui = ctx.ui
        service = ctx.service
        lang = ctx.session.language

        contact = self._contact_input(ctx, contact)
        created = service.create(
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
        )
        contact = ContactDTO.from_entity(created)
        ui.print_success(lang, "SUCCESS_CONTACT_CREATED")
        ui.show_contact_detail(lang, contact)
        ui.pause(lang)

    def _contact_input(self, ctx: ContactContext, contact: ContactDTO) -> ContactDTO:
        """Prompt the user for each contact field and return a new DTO."""
        ui = ctx.ui
        lang = ctx.session.language

        contact.first_name = ui.get_input(
            lang,
            "PROMPT_FIRST_NAME",
            default=contact.first_name,
        )
        contact.last_name = ui.get_input(
            lang,
            "PROMPT_LAST_NAME",
            default=contact.last_name,
        )
        contact.email = ui.get_input(
            lang,
            "PROMPT_EMAIL",
            default=contact.email,
        )
        contact.phone = ui.get_input(
            lang,
            "PROMPT_PHONE",
            default=contact.phone,
        )

        return contact


class _FindMenuState(BaseState):
    """State for finding contacts by various criteria."""

    @BaseState.handle_errors
    def run(self, ctx: ContactContext) -> BaseState | None:
        """Execute find menu and search for contacts.

        Args:
            ctx: Application context with UI and service.

        Returns:
            Next state based on search results.
        """
        ui = ctx.ui
        service = ctx.service
        lang = ctx.session.language

        option_id = ui.show_find_contact_menu(lang)

        if option_id == "full_name":
            full_name = ui.get_input(lang, "PROMPT_SEARCH_FULL_NAME")
            contacts = [
                ContactDTO.from_entity(c) for c in service.find_by_name(full_name)
            ]
            return _SelectContactState(contacts)

        if option_id == "email":
            email = ui.get_input(lang, "PROMPT_SEARCH_EMAIL")
            contact = ContactDTO.from_entity(service.find_by_email(email))
            return _ContactMenuState(contact, back=MainContactMenuState())

        if option_id == "phone":
            phone = ui.get_input(lang, "PROMPT_SEARCH_PHONE")
            contact = ContactDTO.from_entity(service.find_by_phone(phone))
            return _ContactMenuState(contact, back=MainContactMenuState())

        if option_id == "return":
            return MainContactMenuState()

        return self


@dataclass
class _ListContactsState(BaseState):
    """State for listing contacts with pagination support.

    Uses offset-based paging with a default page size of 20. Interactive
    pagination actions are shown only when total results are greater than 10.
    """

    offset: int = 0
    limit: int = PAGINATION.CONTACTS_PAGE_SIZE
    pagination_threshold: int = PAGINATION.CONTACTS_THRESHOLD

    @BaseState.handle_errors
    def run(self, ctx: ContactContext) -> BaseState | None:
        """Render paginated contact list and handle page navigation.

        The table footer shows current page, total pages, and item range.
        """
        ui = ctx.ui
        service = ctx.service
        lang = ctx.session.language

        result = service.list_contacts(limit=self.limit, offset=self.offset)
        page = ContactPageDTO(
            contacts=[ContactDTO.from_entity(c) for c in result.contacts],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
        )
        ui.show_contacts_table(
            lang,
            page.contacts,
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )

        if page.total <= self.pagination_threshold:
            ui.pause(lang)
            return MainContactMenuState()

        option_id = ui.show_contact_list_pagination_menu(
            language=lang,
            has_previous=page.has_previous,
            has_next=page.has_next,
        )

        if option_id == "next" and page.has_next:
            self.offset += page.limit
            return self

        if option_id == "previous" and page.has_previous:
            self.offset = max(0, self.offset - page.limit)
            return self

        return MainContactMenuState()


@dataclass
class _SelectContactState(BaseState):
    """State for selecting a contact from search results.

    Attributes:
        contacts: List of contacts to choose from.
    """

    contacts: Sequence[ContactDTO]
    offset: int = 0
    limit: int = PAGINATION.CONTACTS_PAGE_SIZE

    def run(self, ctx: ContactContext) -> BaseState | None:
        """Display contact selection menu.

        Args:
            ctx: Application context with UI.

        Returns:
            ContactMenuState for selected contact or FindMenuState.
        """
        ui = ctx.ui
        lang = ctx.session.language

        if len(self.contacts) <= self.limit:
            option_id = ui.show_select_contact_menu(lang, self.contacts)

            if option_id == "return":
                return _FindMenuState()

            try:
                index = int(option_id)
                contact = self.contacts[index]
            except (ValueError, IndexError):
                return self

            return _ContactMenuState(contact, back=_FindMenuState())

        option_id = ui.show_paginated_select_contact_menu(
            language=lang,
            contacts=self.contacts,
            offset=self.offset,
            limit=self.limit,
        )

        if option_id == "return":
            return _FindMenuState()

        has_previous = self.offset > 0
        has_next = (self.offset + self.limit) < len(self.contacts)

        if option_id == "previous" and has_previous:
            self.offset = max(0, self.offset - self.limit)
            return self

        if option_id == "next" and has_next:
            self.offset += self.limit
            return self

        try:
            index = int(option_id)
            contact = self.contacts[index]
        except (ValueError, IndexError):
            return self

        return _ContactMenuState(contact, back=_FindMenuState())


@dataclass
class _ContactMenuState(MainContactMenuState):
    """State for viewing, editing, or deleting a single contact.

    Attributes:
        contact: Contact being viewed/edited.
        back: State to return to when done.
    """

    contact: ContactDTO
    back: BaseState

    @BaseState.handle_errors
    def run(self, ctx: ContactContext) -> BaseState | None:
        """Execute contact menu and handle view/edit/delete.

        Args:
            ctx: Application context with UI and service.

        Returns:
            Next state based on user action.
        """
        ui = ctx.ui
        lang = ctx.session.language

        option_id = ui.show_contact_menu(lang)

        if option_id == "view":
            ui.show_contact_detail(lang, self.contact)
            ui.pause(lang)
            return self

        if option_id == "edit":
            edited_contact = self._edit_contact(ctx, self.contact)
            if edited_contact is None:
                return self.back
            self.contact = edited_contact
            return self

        if option_id == "del":
            if not self._delete_contact(ctx, self.contact.contact_id):
                return self
            return self.back

        if option_id == "return":
            return self.back

        return self

    @BaseState.handle_errors
    def _edit_contact(
        self, ctx: ContactContext, contact: ContactDTO
    ) -> ContactDTO | None:
        """Prompt for updated data, persist changes, and show confirmation."""
        ui = ctx.ui
        service = ctx.service
        lang = ctx.session.language

        contact = self._contact_input(ctx, contact)
        updated = service.update(
            contact_id=contact.contact_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
        )
        contact = ContactDTO.from_entity(updated)
        ui.print_success(lang, "SUCCESS_CONTACT_UPDATED")
        ui.show_contact_detail(lang, contact)
        ui.pause(lang)
        return contact

    def _delete_contact(self, ctx: ContactContext, contact_id: int) -> bool:
        """Ask for confirmation and soft-delete the contact."""
        ui = ctx.ui
        service = ctx.service
        lang = ctx.session.language

        if ui.confirm(lang, "CONFIRM_DELETE_CONTACT"):
            if service.delete(contact_id):
                ui.print_success(lang, "SUCCESS_CONTACT_DELETED")
            else:
                ui.print_warning(lang, "DELETE_NOT_FOUND")
        else:
            ui.cancel(lang)
            return False

        ui.pause(lang)
        return True
