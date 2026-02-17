#!/usr/bin/env python3
"""Base service class for the application layer.

Provides a generic abstract base that concrete services (e.g.
``ContactService``) inherit from. Adapters depend on the
``Service`` protocol defined in ``core.interfaces``; this base
class satisfies that protocol.
"""

from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from archive_manager.core.interfaces import Repository, Service

TRepository = TypeVar("TRepository", bound=Repository)


class BaseService(ABC, Service, Generic[TRepository]):
    """Generic service base class for business logic layer.

    Satisfies the ``Service`` protocol structurally and provides
    generic repository typing plus ``__init__`` so that concrete
    subclasses only need to set ``NAME`` and implement business methods.

    Attributes:
        NAME: Service name identifier.
        _repo: Repository instance for data access.
    """

    NAME: str
    _repo: TRepository

    def __init__(self, repository: TRepository) -> None:
        """Initialize the service with the given repository.

        Args:
            repository: Repository instance for data access.
        """
        self._repo = repository
