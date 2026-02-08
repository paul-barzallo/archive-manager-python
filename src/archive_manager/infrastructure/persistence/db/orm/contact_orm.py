#!/usr/bin/env python3
"""SQLAlchemy ORM model for Contact entities."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from archive_manager.infrastructure.persistence.db.orm.base_orm import BaseORM


class ContactORM(BaseORM):
    """SQLAlchemy ORM model mapped to the ``contacts`` table."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    __table_args__ = (
        Index(
            "idx_contacts_email_unique",
            "email",
            unique=True,
            sqlite_where=deleted_at.is_(None),
        ),
        Index(
            "idx_contacts_phone_unique",
            "phone",
            unique=True,
            sqlite_where=(deleted_at.is_(None)) & (phone != ""),
        ),
        Index("idx_contacts_first_name", "first_name"),
        Index("idx_contacts_last_name", "last_name"),
        Index("idx_contacts_full_name", "first_name", "last_name"),
        Index("idx_contacts_active", "deleted_at"),
    )

    @property
    def is_deleted(self) -> bool:
        """Return whether the contact has been soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark the contact as deleted."""
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """Clear the deleted flag."""
        self.deleted_at = None

    def __repr__(self) -> str:
        """Return a string representation of the ContactORM instance."""
        deleted_str = " [DELETED]" if self.is_deleted else ""
        return (
            f"ContactORM(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}'{deleted_str})"
        )
