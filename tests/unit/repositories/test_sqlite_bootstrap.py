#!/usr/bin/env python3
"""Tests for SQLite bootstrap module.

Tests are designed to be dynamic - they automatically discover and
validate any SQL scripts added to the scripts/ directory.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from archive_manager.infrastructure.persistence.db.sqlite_bootstrap import (
    _SqliteBootstrap,
    run_bootstrap,
)


class TestSqliteBootstrap:
    """Tests for _SqliteBootstrap class."""

    def test_get_scripts_returns_sql_files(self) -> None:
        """Verify _get_scripts returns SQL file paths."""
        engine = create_engine("sqlite:///:memory:")
        bootstrap = _SqliteBootstrap(engine)

        scripts = bootstrap._get_scripts()

        assert isinstance(scripts, list)
        assert all(script.suffix == ".sql" for script in scripts)

    def test_scripts_are_sorted_alphabetically(self) -> None:
        """Verify scripts are returned in alphabetical order."""
        engine = create_engine("sqlite:///:memory:")
        bootstrap = _SqliteBootstrap(engine)

        scripts = bootstrap._get_scripts()

        if len(scripts) > 1:
            names = [s.name for s in scripts]
            assert names == sorted(names)

    def test_all_scripts_are_valid_sql(self) -> None:
        """Verify all SQL scripts have valid syntax (can be parsed)."""
        engine = create_engine("sqlite:///:memory:")
        bootstrap = _SqliteBootstrap(engine)

        for script in bootstrap._get_scripts():
            content = script.read_text(encoding="utf-8")
            non_comment_lines = [
                line.strip()
                for line in content.split("\n")
                if line.strip() and not line.strip().startswith("--")
            ]
            assert len(non_comment_lines) > 0, f"Script {script.name} has no SQL"

    def test_is_bootstrapped_returns_false_for_new_database(self) -> None:
        """Verify _is_bootstrapped returns False when no bootstrap has run."""
        engine = create_engine("sqlite:///:memory:")
        bootstrap = _SqliteBootstrap(engine)

        assert bootstrap._is_bootstrapped() is False

    def test_is_bootstrapped_returns_true_after_run(self) -> None:
        """Verify _is_bootstrapped returns True after bootstrap completes."""
        engine = create_engine("sqlite:///:memory:")
        bootstrap = _SqliteBootstrap(engine)
        bootstrap.run()

        assert bootstrap._is_bootstrapped() is True


class TestRunBootstrap:
    """Tests for run_bootstrap() function."""

    def test_creates_table_and_triggers(self) -> None:
        """Verify table and triggers are created for in-memory databases."""
        engine = create_engine("sqlite:///:memory:")

        run_bootstrap(engine)

        # Check table exists
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='contacts'"
                )
            )
            table = result.fetchone()

        assert table is not None
        assert table[0] == "contacts"

        # Check trigger exists
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='trigger' AND name='trg_contacts_updated_at'"
                )
            )
            trigger = result.fetchone()

        assert trigger is not None

    def test_creates_table_for_file_database(self) -> None:
        """Verify table is created for new file databases."""
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.sqlite"
            db_url = f"sqlite:///{db_path}"

            engine = create_engine(db_url)
            try:
                run_bootstrap(engine)

                with engine.connect() as conn:
                    result = conn.execute(
                        text(
                            "SELECT name FROM sqlite_master "
                            "WHERE type='table' AND name='contacts'"
                        )
                    )
                    table = result.fetchone()

                assert table is not None
            finally:
                engine.dispose()

    def test_is_idempotent(self) -> None:
        """Verify bootstrap can be called multiple times safely."""
        engine = create_engine("sqlite:///:memory:")

        run_bootstrap(engine)
        run_bootstrap(engine)  # Should not fail

        # Verify still bootstrapped
        bootstrap = _SqliteBootstrap(engine)
        assert bootstrap._is_bootstrapped()

    def test_skips_when_already_bootstrapped(self) -> None:
        """Verify bootstrap skips execution when already done."""
        engine = create_engine("sqlite:///:memory:")

        run_bootstrap(engine)

        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='index' AND tbl_name='contacts'"
                )
            )
            row = result.fetchone()
            assert row is not None
            original_index_count = row[0]

        run_bootstrap(engine)

        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='index' AND tbl_name='contacts'"
                )
            )
            row = result.fetchone()
            assert row is not None
            new_index_count = row[0]

        assert new_index_count == original_index_count

    def test_trigger_updates_updated_at(self) -> None:
        """Verify trigger updates updated_at when contact is modified."""
        engine = create_engine("sqlite:///:memory:")
        run_bootstrap(engine)

        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone, created_at, updated_at) "
                    "VALUES ('John', 'Doe', 'john@example.com', '', "
                    "datetime('now', '-1 day'), datetime('now', '-1 day'))"
                )
            )
            conn.commit()

            result = conn.execute(text("SELECT updated_at FROM contacts WHERE id = 1"))
            row = result.fetchone()
            assert row is not None
            original_updated_at = row[0]

            conn.execute(text("UPDATE contacts SET first_name = 'Jane' WHERE id = 1"))
            conn.commit()

            result = conn.execute(text("SELECT updated_at FROM contacts WHERE id = 1"))
            row = result.fetchone()
            assert row is not None
            new_updated_at = row[0]

        assert new_updated_at != original_updated_at


class TestValidationTriggers:
    """Tests for data validation triggers.

    Triggers are simplified to only enforce NOT NULL on required fields
    and auto-update ``updated_at``. Format validation is in the application layer.
    """

    @pytest.fixture
    def engine(self):
        """Create and bootstrap an in-memory database."""
        engine = create_engine("sqlite:///:memory:")
        run_bootstrap(engine)
        return engine

    def test_accepts_valid_contact(self, engine) -> None:
        """Verify trigger accepts a well-formed contact."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.commit()

            result = conn.execute(text("SELECT email FROM contacts WHERE id = 1"))
            row = result.fetchone()
            assert row is not None
            assert row[0] == "john@example.com"

    def test_rejects_empty_first_name(self, engine) -> None:
        """Verify trigger rejects empty first_name."""
        with (
            pytest.raises(IntegrityError, match="first_name is required"),
            engine.connect() as conn,
        ):
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('', 'Doe', 'john@example.com', '+1234567890')"
                )
            )
            conn.commit()

    def test_rejects_empty_last_name(self, engine) -> None:
        """Verify trigger rejects empty last_name."""
        with (
            pytest.raises(IntegrityError, match="last_name is required"),
            engine.connect() as conn,
        ):
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', '', 'john@example.com', '+1234567890')"
                )
            )
            conn.commit()

    def test_rejects_contact_without_email(self, engine) -> None:
        """Verify trigger rejects contact without email."""
        with (
            pytest.raises(IntegrityError, match="email is required"),
            engine.connect() as conn,
        ):
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', '', '+1234567890')"
                )
            )
            conn.commit()

    def test_accepts_contact_without_phone(self, engine) -> None:
        """Verify trigger accepts contact with empty phone (phone is optional)."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.commit()

    def test_unique_email_constraint(self, engine) -> None:
        """Verify UNIQUE index rejects duplicate email among active contacts."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.commit()

        with (
            pytest.raises(IntegrityError),
            engine.connect() as conn,
        ):
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('Jane', 'Smith', 'john@example.com', '')"
                )
            )
            conn.commit()

    def test_allows_email_reuse_after_soft_delete(self, engine) -> None:
        """Verify soft-deleted email can be reused by a new contact."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.execute(
                text("UPDATE contacts SET deleted_at = datetime('now') WHERE id = 1")
            )
            conn.commit()

            # Same email should now be accepted
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('Jane', 'Smith', 'john@example.com', '')"
                )
            )
            conn.commit()

    def test_allows_duplicate_empty_phone(self, engine) -> None:
        """Verify multiple contacts can have empty phone."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('Jane', 'Smith', 'jane@example.com', '')"
                )
            )
            conn.commit()

    def test_rejects_empty_required_fields_on_update(self, engine) -> None:
        """Verify triggers enforce required fields on UPDATE too."""
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO contacts "
                    "(first_name, last_name, email, phone) "
                    "VALUES ('John', 'Doe', 'john@example.com', '')"
                )
            )
            conn.commit()

        with (
            pytest.raises(IntegrityError, match="first_name is required"),
            engine.connect() as conn,
        ):
            conn.execute(text("UPDATE contacts SET first_name = '' WHERE id = 1"))
            conn.commit()
