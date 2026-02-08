#!/usr/bin/env python3
"""Protocol definition for Contact repository implementations.

The repository layer provides a domain-focused interface for contact
persistence, abstracting away storage details through the Repository
pattern combined with Protocol typing for flexibility.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from archive_manager.core.entities import Contact
from archive_manager.core.interfaces.repository import Repository


@runtime_checkable
class ContactRepository(Repository, Protocol):
    """Protocol for Contact repository operations.

    Defines the contract that all repository implementations must follow.
    Repositories handle persistence of Contact entities and provide
    domain-focused query methods.

    Implementations:
    - ``SqliteContactRepository``: SQL database storage (SQLite by default)
    """

    def add(self, contact: Contact) -> Contact:
        """Persist a new contact and return the stored entity.

        Args:
            contact: Contact entity to persist.

        Returns:
            Contact: Stored contact entity with repository-assigned fields.

        Raises:
            AppError: If a uniqueness constraint is violated.
            AppInfrastructureError: If persistence fails.
        """
        ...

    def find_by_name(self, full_name: str) -> Sequence[Contact]:
        """Find contacts by full name with partial matching.

        Args:
            full_name: Full name or partial name query.

        Returns:
            Sequence[Contact]: Sequence of matching Contact entities.

        Raises:
            AppInfrastructureError: If a persistence error occurs.
        """
        ...

    def find_by_email(self, email: str) -> Contact | None:
        """Find a contact by email address (exact match).

        Args:
            email: Email address to search for.

        Returns:
            Contact | None: Matching contact if found, otherwise None.

        Raises:
            AppInfrastructureError: If a persistence error occurs.
        """
        ...

    def find_by_phone(self, phone: str) -> Contact | None:
        """Find a contact by phone number (exact canonical match).

        Args:
            phone: Phone number in canonical form to search for.

        Returns:
            Contact | None: Matching contact if found, otherwise None.

        Raises:
            AppInfrastructureError: If a persistence error occurs.
        """
        ...

    def update(self, contact: Contact) -> Contact:
        """Update an existing contact and return the stored entity.

        Args:
            contact: Contact entity containing updated values.

        Returns:
            Contact: Updated contact as stored by the repository.

        Raises:
            AppError: If contact not found or uniqueness violated.
            AppInfrastructureError: If persistence fails.
        """
        ...

    def delete(self, contact_id: int) -> bool:
        """Delete a contact by its identifier.

        Args:
            contact_id: Identifier of the contact to delete.

        Returns:
            True if contact was deleted, False if not found.

        Raises:
            AppInfrastructureError: If persistence fails.
        """
        ...

    def list_all(self) -> Sequence[Contact]:
        """Get all contacts.

        Returns:
            Sequence[Contact]: All stored contacts (may be empty).

        Raises:
            AppInfrastructureError: If persistence fails.
        """
        ...
