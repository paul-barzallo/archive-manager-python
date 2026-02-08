#!/usr/bin/env python3
"""Business policy validation for contacts."""

from __future__ import annotations

from archive_manager.core.entities import Contact
from archive_manager.core.errors import AppError


class ContactPolicy:
    """Validates business rules for contact uniqueness."""

    def __init__(self) -> None:
        """Initialize validator instance."""
        self.errors: list[AppError] = []

    def ensure_unique_email(
        self,
        contact_found: Contact | None,
        actual_contact: Contact | None = None,
    ) -> None:
        """Validate that the email is not duplicated.

        Args:
            contact_found: Contact found with the same email.
            actual_contact: The actual contact being created or updated.
        """
        if self._contact_exists(contact_found, actual_contact):
            self.errors.append(
                AppError(
                    code="DUPLICATE_EMAIL",
                    origin="ContactPolicy.ensure_unique_email",
                    field="email",
                    email=contact_found.email if contact_found else "",
                )
            )

    def ensure_unique_phone(
        self,
        contact_found: Contact | None,
        actual_contact: Contact | None = None,
    ) -> None:
        """Validate that the phone is not duplicated.

        Args:
            contact_found: Contact found with the same phone.
            actual_contact: The actual contact being created or updated.
        """
        if self._contact_exists(contact_found, actual_contact):
            self.errors.append(
                AppError(
                    code="DUPLICATE_PHONE",
                    origin="ContactPolicy.ensure_unique_phone",
                    field="phone",
                    phone=contact_found.phone if contact_found else "",
                )
            )

    def _contact_exists(
        self,
        contact_found: Contact | None,
        actual_contact: Contact | None,
    ) -> bool:
        """Return ``True`` if a different contact already uses the value."""
        if contact_found and actual_contact is not None:
            return contact_found != actual_contact
        return contact_found is not None
