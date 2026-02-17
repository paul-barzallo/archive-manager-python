#!/usr/bin/env python3
"""Dependency wiring for API adapter."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, cast

from fastapi import Request

from archive_manager.application.services import ContactService
from archive_manager.infrastructure.config import Settings
from archive_manager.infrastructure.persistence import SqliteContactRepository
from archive_manager.infrastructure.persistence.db import SqliteConnection


class Container(Protocol):
    """Protocol for dependency containers."""

    @property
    def contact_service(self) -> ContactService:
        """Contact service instance."""
        ...

    def close(self) -> None:
        """Release container resources."""
        ...


class BaseApiContainer(ABC, Container):
    """Base implementation for API containers."""

    @abstractmethod
    def close(self) -> None:
        """Release container resources."""
        ...


@dataclass
class ApiContainer(BaseApiContainer):
    """Container for long-lived API dependencies."""

    _contact_service: ContactService
    _connection: SqliteConnection

    @property
    def contact_service(self) -> ContactService:
        """Contact service instance."""
        return self._contact_service

    @classmethod
    def build(cls, settings: Settings) -> ApiContainer:
        """Build all adapter dependencies from application settings.

        Args:
            settings: Application settings object.

        Returns:
            Fully wired API dependency container.
        """
        connection = SqliteConnection(settings.database)
        repo = SqliteContactRepository(connection)
        service = ContactService(repo)
        return cls(_contact_service=service, _connection=connection)

    def close(self) -> None:
        """Release container resources."""
        self._connection.close()


def get_contact_service(request: Request) -> ContactService:
    """Return contact service from current app state.

    Args:
        request: FastAPI request object.

    Returns:
        Contact service instance bound to current app container.
    """
    container = cast(ApiContainer, request.app.state.container)
    return container.contact_service
