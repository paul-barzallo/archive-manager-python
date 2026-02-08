#!/usr/bin/env python3
"""Contact domain entity."""

from __future__ import annotations

from typing import Self

from archive_manager.core.entities.base_entity import BaseEntity
from archive_manager.core.entities.validators import ContactValidator
from archive_manager.core.errors import AppValidationErrors


class Contact(BaseEntity):
    """Domain entity representing a single contact.

    Inherits from BaseEntity which provides:
    - Blocked ``__init__`` (must use factory methods)
    - Abstract ``create()`` and ``from_persistence()`` methods

    It should NOT contain persistence logic (TXT/SQL/JSON), which belongs
    to repositories/mappers.
    """

    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone: str

    @classmethod
    def create(
        cls,
        *,
        contact_id: int = 0,
        first_name: str,
        last_name: str,
        email: str,
        phone: str = "",
    ) -> Self:
        """Create a contact from user input with full validation.

        Validates all fields, then canonicalises the phone number for
        storage (digits + optional leading ``+``).

        Args:
            contact_id: Unique identifier (0 for new, > 0 for updates).
            first_name: Contact's first name (required).
            last_name: Contact's last name (required).
            email: Contact's email address (required).
            phone: Contact's phone number (optional).

        Returns:
            A validated Contact instance.

        Raises:
            AppValidationErrors: If any field validation fails.
        """
        validator = ContactValidator()
        validated_first = validator.validate_first_name(first_name, required=True)
        validated_last = validator.validate_last_name(last_name, required=True)
        validated_email = validator.validate_email(email, required=True)
        validated_phone = validator.validate_phone(phone, required=False)

        if validator.errors:
            raise AppValidationErrors(validator.errors, origin="Contact.create")

        instance = cls.__new__(cls)
        instance.contact_id = contact_id
        instance.first_name = validated_first
        instance.last_name = validated_last
        instance.email = validated_email
        instance.phone = ContactValidator.canonicalize_phone(validated_phone)
        return instance

    @classmethod
    def from_persistence(
        cls,
        *,
        contact_id: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
    ) -> Self:
        """Reconstruct a contact from persistence layer.

        No validation is performed since data integrity is assumed.
        Phone is already stored in canonical form.

        Args:
            contact_id: Unique identifier from database.
            first_name: Contact's first name.
            last_name: Contact's last name.
            email: Contact's email address.
            phone: Contact's phone number (canonical form).

        Returns:
            A reconstructed Contact instance.
        """
        instance = cls.__new__(cls)
        instance.contact_id = contact_id
        instance.first_name = first_name
        instance.last_name = last_name
        instance.email = email
        instance.phone = phone
        return instance

    def __repr__(self) -> str:
        """Return a Python-evaluable string representation of the contact.

        Returns:
            str: String in format Contact(contact_id=1, first_name='john', ...).
        """
        return (
            f"Contact(contact_id={self.contact_id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"email={self.email!r}, "
            f"phone={self.phone!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two Contact instances for equality based on their IDs.

        Args:
            other: The other Contact instance to compare with.

        Returns:
            ``True`` if both contacts have the same ID, ``False`` otherwise.
        """
        if not isinstance(other, Contact):
            return NotImplemented
        return self.contact_id == other.contact_id
