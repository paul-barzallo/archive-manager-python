#!/usr/bin/env python3
"""Data Transfer Object for Contact entities."""

from __future__ import annotations

from dataclasses import dataclass

from archive_manager.core.entities import Contact


@dataclass
class ContactDTO:
    """Data Transfer Object for Contact entity."""

    contact_id: int = 0
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""

    def as_fields(self) -> tuple[dict[str, str], ...]:
        """Return fields as a tuple of code-value dicts for detail views."""
        return (
            {"code": "DETAIL_FIRST_NAME", "value": self.first_name},
            {"code": "DETAIL_LAST_NAME", "value": self.last_name},
            {"code": "DETAIL_EMAIL", "value": self.email},
            {"code": "DETAIL_PHONE", "value": self.phone},
        )

    def to_dict(self) -> dict[str, str | int]:
        """Convert DTO to a plain dictionary."""
        return {
            "contact_id": self.contact_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
        }

    @staticmethod
    def from_entity(contact: Contact) -> ContactDTO:
        """Create a DTO from a domain entity."""
        return ContactDTO(
            contact_id=contact.contact_id,
            first_name=contact.first_name.title(),
            last_name=contact.last_name.title(),
            email=contact.email,
            phone=contact.phone,
        )
