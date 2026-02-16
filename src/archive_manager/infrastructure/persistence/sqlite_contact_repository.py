#!/usr/bin/env python3
"""SQLite repository implementation for contacts."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from archive_manager.core.entities import Contact
from archive_manager.core.errors import AppError, AppInfrastructureError
from archive_manager.infrastructure.persistence.base_contact_repository import (
    BaseContactRepository,
)
from archive_manager.infrastructure.persistence.db import ContactORM, SqliteConnection
from archive_manager.infrastructure.persistence.mappers import ContactMapper

logger = logging.getLogger(__name__)


class SqliteContactRepository(BaseContactRepository[SqliteConnection]):
    """SQLite repository implementing ContactRepository protocol."""

    def add(self, contact: Contact) -> Contact:
        """Add a new contact to the database.

        Args:
            contact: Contact entity to persist.

        Returns:
            Contact with assigned ID.

        Raises:
            AppError: If email or phone already exists.
            AppInfrastructureError: On database errors.
        """
        try:
            with self._db.get_session() as session:
                orm = ContactMapper.to_orm(contact)
                session.add(orm)
                session.flush()
                contact = ContactMapper.from_orm(orm)

        except IntegrityError as exc:
            self._raise_duplicate_error(
                exc,
                email=contact.email,
                phone=contact.phone,
                origin="SqliteContactRepository.add",
            )

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.add",
                message=str(exc),
            ) from exc

        return contact

    def get(self, contact_id: int) -> Contact | None:
        """Find a contact by ID.

        Args:
            contact_id: Contact identifier.

        Returns:
            Matching contact or ``None``.
        """
        try:
            with self._db.get_session() as session:
                orm = session.get(ContactORM, contact_id)
                if not orm or orm.deleted_at:
                    return None
                return ContactMapper.from_orm(orm)

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.get",
                message=str(exc),
            ) from exc

    def find_by_name(self, full_name: str) -> Sequence[Contact]:
        """Find contacts by partial name match.

        Args:
            full_name: Search string for full name (first + last).

        Returns:
            Sequence of matching contacts.
        """
        try:
            with self._db.get_session() as session:
                full_expr = ContactORM.first_name + " " + ContactORM.last_name
                search = f"%{full_name}%"

                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .where(full_expr.like(search))
                )

                results = session.execute(stmt).scalars().all()
                return [ContactMapper.from_orm(orm) for orm in results]

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.find_by_name",
                message=str(exc),
            ) from exc

    def find_by_email(self, email: str) -> Contact | None:
        """Find a contact by exact email match.

        Args:
            email: Email address to search for.

        Returns:
            Matching contact or ``None`` if not found.
        """
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .where(ContactORM.email == email.strip())
                )
                orm = session.execute(stmt).scalar_one_or_none()
                return ContactMapper.from_orm(orm) if orm else None

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.find_by_email",
                message=str(exc),
            ) from exc

    def find_by_phone(self, phone: str) -> Contact | None:
        """Find a contact by exact canonical phone match.

        Args:
            phone: Phone number in canonical form to search for.

        Returns:
            Matching contact or ``None`` if not found.
        """
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .where(ContactORM.phone == phone.strip())
                )
                orm = session.execute(stmt).scalar_one_or_none()
                return ContactMapper.from_orm(orm) if orm else None

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.find_by_phone",
                message=str(exc),
            ) from exc

    def update(self, contact: Contact) -> Contact:
        """Update an existing contact.

        Args:
            contact: Contact entity with updated data.

        Returns:
            Updated contact entity.

        Raises:
            AppError: If contact not found or email/phone conflicts.
            AppInfrastructureError: On database errors.
        """
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .where(ContactORM.id == contact.contact_id)
                )
                orm = session.execute(stmt).scalar_one_or_none()

                if not orm:
                    raise AppError(
                        "UPDATE_NOT_FOUND",
                        origin="SqliteContactRepository.update",
                        contact_id=contact.contact_id,
                    )

                orm.first_name = contact.first_name
                orm.last_name = contact.last_name
                orm.email = contact.email
                orm.phone = contact.phone

                session.flush()
                contact = ContactMapper.from_orm(orm)

        except AppError:
            raise
        except IntegrityError as exc:
            self._raise_duplicate_error(
                exc,
                email=contact.email,
                phone=contact.phone,
                origin="SqliteContactRepository.update",
            )
        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.update",
                message=str(exc),
            ) from exc

        return contact

    def delete(self, contact_id: int) -> bool:
        """Soft delete a contact by ID.

        Args:
            contact_id: ID of contact to delete.

        Returns:
            True if contact was deleted, False if not found.

        Raises:
            AppInfrastructureError: On database errors.
        """
        logger.debug("Soft deleting contact: id=%d", contact_id)
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .where(ContactORM.id == contact_id)
                )
                orm = session.execute(stmt).scalar_one_or_none()

                if not orm:
                    logger.warning(
                        "Contact with id=%s not found or already deleted.", contact_id
                    )
                    return False

                orm.soft_delete()
                logger.info("Contact soft-deleted: id=%d", contact_id)
                return True

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.delete",
                message=str(exc),
            ) from exc

    def hard_delete(self, contact_id: int) -> None:
        """Permanently delete a contact from database.

        Args:
            contact_id: ID of contact to delete.

        Raises:
            AppInfrastructureError: On database errors.
        """
        logger.warning("HARD DELETE requested for contact: id=%d", contact_id)
        try:
            with self._db.get_session() as session:
                stmt = select(ContactORM).where(ContactORM.id == contact_id)
                orm = session.execute(stmt).scalar_one_or_none()

                if orm:
                    session.delete(orm)
                    logger.warning("Contact PERMANENTLY deleted: id=%d", contact_id)
                else:
                    logger.warning(
                        "Contact with id=%s not found for hard delete.", contact_id
                    )

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.hard_delete",
                message=str(exc),
            ) from exc

    def restore(self, contact_id: int) -> Contact:
        """Restore a soft-deleted contact.

        Args:
            contact_id: ID of contact to restore.

        Returns:
            Restored contact entity.

        Raises:
            AppError: If deleted contact not found.
            AppInfrastructureError: On database errors.
        """
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_not(None))
                    .where(ContactORM.id == contact_id)
                )
                orm = session.execute(stmt).scalar_one_or_none()

                if not orm:
                    raise AppError(
                        "RESTORE_NOT_FOUND",
                        "SqliteContactRepository.restore",
                        contact_id=contact_id,
                    )

                orm.restore()
                session.flush()
                return ContactMapper.from_orm(orm)

        except AppError:
            raise
        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.restore",
                message=str(exc),
            ) from exc

    def list_all(self) -> Sequence[Contact]:
        """List all active (non-deleted) contacts.

        Returns:
            Sequence of all active contacts ordered by ID.
        """
        try:
            with self._db.get_session() as session:
                stmt = (
                    select(ContactORM)
                    .where(ContactORM.deleted_at.is_(None))
                    .order_by(ContactORM.id)
                )
                results = session.execute(stmt).scalars().all()
                return [ContactMapper.from_orm(orm) for orm in results]

        except Exception as exc:
            raise AppInfrastructureError(
                "PERSISTENCE_ERROR",
                "SqliteContactRepository.list_all",
                message=str(exc),
            ) from exc
