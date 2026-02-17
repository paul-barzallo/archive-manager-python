#!/usr/bin/env python3
"""SQLite database bootstrap and initialization."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import text

if TYPE_CHECKING:
    from sqlalchemy import Engine

logger = logging.getLogger(__name__)


class _SqliteBootstrap:
    """Runs SQL bootstrap scripts on first database creation."""

    _SCRIPTS_DIR = Path(__file__).parent / "scripts"

    def __init__(self, engine: Engine) -> None:
        """Initialize with the SQLAlchemy engine to bootstrap."""
        self._engine = engine

    def run(self) -> None:
        """Run bootstrap scripts if the database is not yet initialised."""
        if self._is_bootstrapped():
            logger.debug("Database already bootstrapped: skipping")
            return
        logger.info("Running database bootstrap scripts")
        self._execute_scripts()

    def _is_bootstrapped(self) -> bool:
        """Return ``True`` if the database already contains the contacts table."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='table' AND name='contacts'"
                )
            )
            count = result.scalar()
            return count is not None and count > 0

    def _get_scripts(self) -> list[Path]:
        """Return sorted list of SQL bootstrap scripts."""
        if not self._SCRIPTS_DIR.exists():
            return []
        return sorted(self._SCRIPTS_DIR.glob("*.sql"))

    def _execute_scripts(self) -> None:
        """Execute all bootstrap scripts in order."""
        scripts = self._get_scripts()
        if not scripts:
            logger.warning("No bootstrap scripts found in %s", self._SCRIPTS_DIR)
            return
        for script_path in scripts:
            self._execute_script(script_path)

    def _execute_script(self, script_path: Path) -> None:
        """Parse and execute a single SQL script file."""
        sql_content = script_path.read_text(encoding="utf-8")
        lines = [
            line
            for line in sql_content.split("\n")
            if not line.strip().startswith("--")
        ]
        clean_sql = "\n".join(lines).strip()
        if not clean_sql:
            return
        statements = self._split_statements(clean_sql)
        with self._engine.connect() as conn:
            for statement in statements:
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        logger.debug("Executed bootstrap script: %s", script_path.name)

    def _split_statements(self, sql: str) -> list[str]:
        """Split SQL text into individual statements.

        Handles multi-line ``BEGIN...END`` blocks (triggers) correctly.
        """
        statements: list[str] = []
        current: list[str] = []
        in_block = False

        for line in sql.split("\n"):
            stripped = line.strip().upper()

            if "BEGIN" in stripped and not in_block:
                in_block = True
            if stripped.startswith("END"):
                in_block = False
                current.append(line)
                statements.append("\n".join(current))
                current = []
                continue

            if in_block:
                current.append(line)
            else:
                if ";" in line:
                    parts = line.split(";")
                    for i, part in enumerate(parts):
                        if i < len(parts) - 1:
                            current.append(part)
                            statements.append("\n".join(current))
                            current = []
                        elif part.strip():
                            current.append(part)
                else:
                    current.append(line)

        if current:
            remaining = "\n".join(current).strip()
            if remaining:
                statements.append(remaining)

        return statements


def run_bootstrap(engine: Engine) -> None:
    """Public entry point for database bootstrap."""
    _SqliteBootstrap(engine).run()
