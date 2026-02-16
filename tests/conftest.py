#!/usr/bin/env python3
"""Test configuration and fixtures.

This module provides shared fixtures for all tests:
- Database connections (in-memory for isolation)
- Repository instances
- Service instances
- Settings configurations

Note on logging language:
    All log messages in test code are in English by design.
    Internationalization is only for user-facing presentation layer.
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# Ensure 'src' is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# ==============================================================================
# Settings & i18n bootstrap
# ==============================================================================


@pytest.fixture(scope="session", autouse=True)
def _configure_i18n():
    """Configure i18n subsystem once for the whole test session."""
    from archive_manager.infrastructure.config import Settings
    from archive_manager.infrastructure.i18n import I18nMenus, I18nMessages, I18nTables

    settings = Settings.for_testing()
    I18nMessages.configure(settings.i18n)
    I18nMenus.configure(settings.i18n)
    I18nTables.configure(settings.i18n)
    yield


@pytest.fixture(scope="session")
def test_settings():
    """Create test-optimized settings (session-scoped for performance)."""
    from archive_manager.infrastructure.config import Settings

    return Settings.for_testing()


# ==============================================================================
# Database Fixtures
# ==============================================================================


@pytest.fixture
def sqlite_connection():
    """Create a fresh in-memory SQLite connection for each test.

    This fixture provides complete isolation between tests by using
    an in-memory database that is destroyed after each test.
    """
    from archive_manager.infrastructure.persistence.db import SqliteConnection

    db = SqliteConnection("sqlite:///:memory:")
    yield db
    db.close()


@pytest.fixture
def sql_repository(sqlite_connection):
    """Create a SQL repository with in-memory database for testing."""
    from archive_manager.infrastructure.persistence import SqliteContactRepository

    return SqliteContactRepository(sqlite_connection)


# ==============================================================================
# Service Fixtures
# ==============================================================================


@pytest.fixture
def service(sql_repository):
    """Create a ContactService with SQL repository."""
    from archive_manager.application.services import ContactService

    return ContactService(repository=sql_repository)


# ==============================================================================
# Entity Fixtures
# ==============================================================================


@pytest.fixture
def sample_contact():
    """Create a basic sample contact for testing."""
    from archive_manager.core.entities import Contact

    return Contact.create(
        first_name="john",
        last_name="doe",
        email="john.doe@example.com",
        phone="1234567890",
    )


@pytest.fixture
def sample_contacts(sql_repository) -> Generator[list, None, None]:
    """Create multiple sample contacts in the database.

    Returns a list of 5 contacts with various characteristics:
    - Ana López (Spanish name with accents)
    - Bob Smith (basic ASCII)
    - José García (Spanish name with accents)
    - Marie-Claire O'Brien (hyphen and apostrophe)
    - David Müller (German umlauts)
    """
    from archive_manager.core.entities import Contact

    contacts_data = [
        ("ana", "lópez", "ana@example.com", "+34600000001"),
        ("bob", "smith", "bob@example.com", "+1234567001"),
        ("josé", "garcía", "jose@example.com", "+34600000002"),
        ("marie-claire", "o'brien", "marie@example.com", "+33123456789"),
        ("david", "müller", "david@example.com", "+49123456789"),
    ]

    created = []
    for first, last, email, phone in contacts_data:
        contact = Contact.create(
            first_name=first, last_name=last, email=email, phone=phone
        )
        saved = sql_repository.add(contact)
        created.append(saved)

    yield created


# ==============================================================================
# Markers
# ==============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for isolated components")
    config.addinivalue_line("markers", "integration: Integration tests across layers")
    config.addinivalue_line("markers", "slow: Tests that take significant time to run")
    config.addinivalue_line("markers", "security: Security-related tests")
