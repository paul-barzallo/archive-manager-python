"""Mapper between Contact domain entities and ORM models."""

from __future__ import annotations

from archive_manager.core.entities import Contact
from archive_manager.infrastructure.persistence.db import ContactORM


class ContactMapper:
    """Bidirectional mapper between Contact entities and ContactORM models."""

    @staticmethod
    def to_orm(contact: Contact) -> ContactORM:
        """Convert a domain entity to an ORM model."""
        orm = ContactORM(
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
        )
        if contact.contact_id > 0:
            orm.id = contact.contact_id
        return orm

    @staticmethod
    def from_orm(orm: ContactORM) -> Contact:
        """Convert an ORM model to a domain entity."""
        return Contact.from_persistence(
            contact_id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            phone=orm.phone,
        )
