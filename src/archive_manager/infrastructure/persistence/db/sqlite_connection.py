#!/usr/bin/env python3
"""SQLite database connection management.

Receives ``DatabaseSettings`` explicitly — no global singleton dependency.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

from archive_manager.core.interfaces import DBConnection
from archive_manager.infrastructure.config import DatabaseSettings
from archive_manager.infrastructure.persistence.db.sqlite_bootstrap import (
    run_bootstrap,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _enable_wal_mode(dbapi_conn: Any, connection_record: Any) -> None:
    """Enable WAL journal mode and foreign keys on a new SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    logger.debug("SQLite WAL mode enabled")


class SqliteConnection(DBConnection):
    """SQLite database connection with SQLAlchemy engine management."""

    def __init__(self, database_settings: DatabaseSettings | str) -> None:
        """Initialize connection from explicit settings or a raw URL.

        Args:
            database_settings: ``DatabaseSettings`` object **or** a plain
                database URL string (e.g. ``"sqlite:///:memory:"``).
                The string form is mainly intended for tests.
        """
        if isinstance(database_settings, str):
            database_url = database_settings
            pool_size = 5
            max_overflow = 10
            pool_recycle = 3600
            echo = False
        else:
            database_url = database_settings.url
            pool_size = database_settings.pool_size
            max_overflow = database_settings.max_overflow
            pool_recycle = database_settings.pool_recycle
            echo = database_settings.echo

        if database_url.startswith("sqlite:///") and ":memory:" not in database_url:
            db_path = Path(database_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

        is_memory = ":memory:" in database_url
        pool_class = StaticPool if is_memory else QueuePool

        engine_kwargs: dict[str, Any] = {
            "poolclass": pool_class,
            "echo": echo,
            "future": True,
        }
        if is_memory:
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow
            engine_kwargs["pool_recycle"] = pool_recycle

        self.engine = create_engine(database_url, **engine_kwargs)
        event.listen(self.engine, "connect", _enable_wal_mode)

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        run_bootstrap(self.engine)
        logger.debug("Database initialized: %s", database_url)

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Provide a transactional session scope."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Dispose of the engine and release all connections."""
        self.engine.dispose()
        logger.debug("Database connection closed")

    def __repr__(self) -> str:
        """Return string representation of the connection."""
        return f"SqliteConnection(engine={self.engine.url})"
