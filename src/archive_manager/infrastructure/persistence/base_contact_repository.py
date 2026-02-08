#!/usr/bin/env python3
"""Abstract base class for Contact repository implementations.

Provides shared infrastructure logic (duplicate detection, error translation)
that all storage backends reuse.  Concrete repositories (e.g.
``SqliteContactRepository``) inherit from this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError

from archive_manager.core.entities import Contact
from archive_manager.core.errors import AppError, AppInfrastructureError
from archive_manager.core.interfaces import ContactRepository, DBConnection

TConnection = TypeVar("TConnection", bound=DBConnection)


class BaseContactRepository(ContactRepository, ABC, Generic[TConnection]):
    """Abstract base providing shared logic for Contact repositories.

    Generic over the database connection type so that subclasses
    can access backend-specific features in a type-safe way.

    Subclasses must implement all CRUD and query methods.
    This base class supplies ``__init__``, ``_is_unique_violation``
    and ``_raise_duplicate_error`` so that every backend translates
    integrity errors uniformly.

    Attributes:
        _db: Database connection instance.
    """

    _db: TConnection

    def __init__(self, connection: TConnection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: Database connection instance.
        """
        self._db = connection

    # ------------------------------------------------------------------
    # Abstract CRUD / query methods
    # ------------------------------------------------------------------

    @abstractmethod
    def add(self, contact: Contact) -> Contact:
        """Persist a new contact.

        See :meth:`ContactRepository.add` for full contract.
        """
        ...

    @abstractmethod
    def find_by_name(self, full_name: str) -> Sequence[Contact]:
        """Find contacts by full name with partial matching.

        See :meth:`ContactRepository.find_by_name` for full contract.
        """
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> Contact | None:
        """Find a contact by exact email address.

        See :meth:`ContactRepository.find_by_email` for full contract.
        """
        ...

    @abstractmethod
    def find_by_phone(self, phone: str) -> Contact | None:
        """Find a contact by canonical phone number.

        See :meth:`ContactRepository.find_by_phone` for full contract.
        """
        ...

    @abstractmethod
    def update(self, contact: Contact) -> Contact:
        """Update an existing contact.

        See :meth:`ContactRepository.update` for full contract.
        """
        ...

    @abstractmethod
    def delete(self, contact_id: int) -> bool:
        """Delete a contact by its identifier.

        See :meth:`ContactRepository.delete` for full contract.
        """
        ...

    @abstractmethod
    def list_all(self) -> Sequence[Contact]:
        """Get all contacts.

        See :meth:`ContactRepository.list_all` for full contract.
        """
        ...

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _is_unique_violation(self, message: str, column: str) -> bool:
        """Check if an IntegrityError is a unique constraint violation.

        Args:
            message: Error message from the database.
            column: Column name to check for.

        Returns:
            ``True`` if the error is a unique violation for the given column.
        """
        # Trigger message: "<column> already exists for another active contact"
        # Index message:   "UNIQUE constraint failed: contacts.<column>"
        return f"{column} already exists" in message or (
            "UNIQUE constraint failed" in message
            and (f"contacts.{column}" in message or column in message)
        )

    def _raise_duplicate_error(
        self, exc: IntegrityError, *, email: str, phone: str, origin: str
    ) -> None:
        """Translate IntegrityError into a domain-specific AppError.

        Args:
            exc: Original database integrity error.
            email: Email address that caused the conflict.
            phone: Phone number that caused the conflict.
            origin: Source location for debugging.

        Raises:
            AppError: For known duplicate violations.
            AppInfrastructureError: For unknown integrity errors.
        """
        message = str(getattr(exc, "orig", exc))
        if self._is_unique_violation(message, "email"):
            raise AppError(
                "DUPLICATE_EMAIL",
                origin=origin,
                field="email",
                email=email,
            ) from exc
        if self._is_unique_violation(message, "phone"):
            raise AppError(
                "DUPLICATE_PHONE",
                origin=origin,
                field="phone",
                phone=phone,
            ) from exc

        raise AppInfrastructureError(
            "PERSISTENCE_ERROR",
            origin,
            message=message,
        ) from exc
