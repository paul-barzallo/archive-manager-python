#!/usr/bin/env python3
"""Console controller for contact management application.

Provides business logic operations for contacts, delegating to ContactService.
Does not handle UI or state machine; those are orchestrated by cli.py.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from archive_manager.adapters.cli.base_controller import BaseCslController
from archive_manager.application.dto import ContactDTO, ContactPageDTO
from archive_manager.application.services import ContactService

logger = logging.getLogger(__name__)


class ContactCslController(BaseCslController[ContactService]):
    """Console-based controller for contact management.

    Provides contact operations delegating to ContactService.
    UI and state machine are handled externally.
    """

    def add_contact(self, contact_dto: ContactDTO) -> ContactDTO:
        """Create a new contact from DTO data.

        Args:
            contact_dto: Contact data transfer object with user input.

        Returns:
            ContactDTO with the created contact's ID assigned.

        Raises:
            AppValidationErrors: If contact data is invalid or duplicate.
        """
        contact = self._service.create(
            first_name=contact_dto.first_name,
            last_name=contact_dto.last_name,
            email=contact_dto.email,
            phone=contact_dto.phone,
        )
        return ContactDTO.from_entity(contact)

    def list_contacts(self, limit: int = 20, offset: int = 0) -> ContactPageDTO:
        """List contacts using a bounded paginated response.

        Args:
            limit: Requested number of returned contacts (max 20).
            offset: Zero-based index for page start.

        Returns:
            Paginated page with contact DTOs and metadata.
        """
        page = self._service.list_contacts(limit=limit, offset=offset)
        contacts = [ContactDTO.from_entity(c) for c in page.contacts]
        return ContactPageDTO(
            contacts=contacts,
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )

    def search_contact_by_name(self, full_name: str) -> Sequence[ContactDTO]:
        """Search contacts by full name (partial match).

        Args:
            full_name: Name or partial name to search for.

        Returns:
            Sequence of matching ContactDTOs.

        Raises:
            AppValidationErrors: If name is invalid.
            AppWarning: If no matches found.
        """
        contacts = self._service.find_by_name(full_name)
        return [ContactDTO.from_entity(c) for c in contacts]

    def search_contact_by_email(self, email: str) -> ContactDTO:
        """Find contact by exact email match.

        Args:
            email: Email address to search.

        Returns:
            Matching ContactDTO.

        Raises:
            AppValidationErrors: If email is invalid.
            AppWarning: If contact not found.
        """
        contact = self._service.find_by_email(email)
        return ContactDTO.from_entity(contact)

    def search_contact_by_phone(self, phone: str) -> ContactDTO:
        """Find contact by exact phone match.

        Args:
            phone: Phone number to search.

        Returns:
            Matching ContactDTO.

        Raises:
            AppValidationErrors: If phone is invalid.
            AppWarning: If contact not found.
        """
        contact = self._service.find_by_phone(phone)
        return ContactDTO.from_entity(contact)

    def edit_contact(self, contact: ContactDTO) -> ContactDTO:
        """Update an existing contact.

        Args:
            contact: ContactDTO with updated data (must have contact_id set).

        Returns:
            Updated ContactDTO.

        Raises:
            AppValidationErrors: If data is invalid or duplicate.
        """
        updated = self._service.update(
            contact.contact_id,
            contact.first_name,
            contact.last_name,
            contact.email,
            contact.phone,
        )
        return ContactDTO.from_entity(updated)

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact by ID."""
        return self._service.delete(contact_id)
