#!/usr/bin/env python3
"""Persistence layer — repository implementations and database access."""

from archive_manager.infrastructure.persistence.sqlite_contact_repository import (
    SqliteContactRepository,
)

__all__ = ["SqliteContactRepository"]
