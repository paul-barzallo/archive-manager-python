#!/usr/bin/env python3
"""Database connection protocol used by repositories.

Defines the contract that any database connection must satisfy.
The application and domain layers depend on this protocol;
infrastructure provides the concrete implementation (e.g. SQLite,
PostgreSQL).
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol


class DBConnection(Protocol):
    """Connection contract for repository access.

    Any database backend must implement this protocol to be usable
    by repositories in the application layer.
    """

    def get_session(self) -> AbstractContextManager[Any]:
        """Return a context-managed session."""
        ...

    def close(self) -> None:
        """Close database connections and cleanup resources."""
        ...
