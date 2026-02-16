#!/usr/bin/env python3
"""Port interfaces (protocols) for the domain layer.

These protocols define contracts that infrastructure and application
implementations must satisfy.  The core layer depends only on these
abstractions, never on concrete implementations.
"""

from .connection import DBConnection
from .contact_repository import ContactRepository
from .entity import Entity
from .repository import Repository
from .service import Service

__all__ = [
    "ContactRepository",
    "DBConnection",
    "Entity",
    "Repository",
    "Service",
]
