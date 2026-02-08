#!/usr/bin/env python3
"""Base entity class for domain objects.

Defines the contract that all domain entities must follow, ensuring consistent
creation patterns with proper validation separation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Self


class BaseEntity(ABC):
    """Abstract base class for domain entities.

    All domain entities must inherit from this class and implement:
    - ``create()``: For creating new entities from user input with full validation
    - ``from_persistence()``: For reconstructing entities from trusted data sources

    Direct instantiation via ``__init__`` is blocked. Use the factory methods.

    This separation ensures:
    - User input is always validated before entity creation
    - Persisted data (already validated) doesn't undergo redundant validation
    - Clear distinction between untrusted and trusted data sources
    """

    def __init__(self) -> None:
        """Blocked. Use ``create()`` or ``from_persistence()`` instead."""
        msg = (
            f"{self.__class__.__name__} cannot be instantiated directly. "
            f"Use {self.__class__.__name__}.create() or "
            f"{self.__class__.__name__}.from_persistence() instead."
        )
        raise TypeError(msg)

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """Create a new entity from user input with full validation.

        This factory method should be used when creating entities from
        external/untrusted sources (forms, APIs, user input, etc.).
        All fields will be validated according to business rules.

        Args:
            *args: Entity fields (implementation-specific).
            **kwargs: Entity fields (implementation-specific).

        Returns:
            A new validated entity instance.

        Raises:
            AppValidationErrors: If any field validation fails.
        """
        ...

    @classmethod
    @abstractmethod
    def from_persistence(cls, *args: Any, **kwargs: Any) -> Self:
        """Reconstruct an entity from a persistence layer.

        This factory method should be used when loading entities from
        trusted sources (database, cache). No validation is performed.

        Args:
            *args: Entity fields (implementation-specific).
            **kwargs: Entity fields (implementation-specific).

        Returns:
            A reconstructed entity instance.
        """
        ...
