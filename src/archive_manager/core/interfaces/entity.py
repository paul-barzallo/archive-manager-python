#!/usr/bin/env python3
"""Entity protocol for the domain layer.

Defines the contract that all domain entities must satisfy.
Concrete entities implement this protocol via the ``BaseEntity``
abstract base class.
"""

from __future__ import annotations

from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class Entity(Protocol):
    """Contract for domain entities.

    Every entity must provide two factory class methods:
    - ``create()``: For new entities from user input (with validation).
    - ``from_persistence()``: For reconstructing from trusted sources.
    """

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """Create a new entity from user input with full validation."""
        ...

    @classmethod
    def from_persistence(cls, *args: Any, **kwargs: Any) -> Self:
        """Reconstruct an entity from a persistence layer."""
        ...
