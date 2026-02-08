#!/usr/bin/env python3
"""Unit tests for SqliteContactRepository."""

import pytest

from archive_manager.core.entities import Contact
from archive_manager.core.errors import AppError
from archive_manager.infrastructure.persistence import SqliteContactRepository
from archive_manager.infrastructure.persistence.db import SqliteConnection


@pytest.fixture
def repository():
    """Create repository instance with fresh in-memory database for each test."""
    db = SqliteConnection("sqlite:///:memory:")
    return SqliteContactRepository(db)


@pytest.fixture
def sample_contact():
    """Create a sample contact for testing."""
    return Contact.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
    )


def test_add_contact(repository, sample_contact):
    """Test adding a new contact."""
    saved = repository.add(sample_contact)

    assert saved.contact_id > 0
    assert saved.first_name == "John"
    assert saved.last_name == "Doe"
    assert saved.email == "john.doe@example.com"


def test_list_all(repository, sample_contact):
    """Test retrieving all contacts."""
    repository.add(sample_contact)

    contacts = repository.list_all()

    assert len(contacts) == 1
    assert contacts[0].email == sample_contact.email


def test_find_by_email(repository, sample_contact):
    """Test finding contact by email."""
    repository.add(sample_contact)

    found = repository.find_by_email("john.doe@example.com")

    assert found is not None
    assert found.first_name == "John"


def test_find_by_phone(repository, sample_contact):
    """Test finding contact by phone (canonical form)."""
    repository.add(sample_contact)

    # Phone is stored canonically: "123-456-7890" → "1234567890"
    found = repository.find_by_phone("1234567890")

    assert found is not None
    assert found.last_name == "Doe"


def test_find_by_name(repository, sample_contact):
    """Test searching contacts by name."""
    repository.add(sample_contact)

    results = repository.find_by_name("John")

    assert len(results) == 1
    assert results[0].first_name == "John"


def test_update_contact(repository, sample_contact):
    """Test updating an existing contact."""
    saved = repository.add(sample_contact)
    saved.phone = "9998887777"

    updated = repository.update(saved)

    assert updated.phone == "9998887777"


def test_delete_contact(repository, sample_contact):
    """Test deleting a contact."""
    saved = repository.add(sample_contact)

    repository.delete(saved.contact_id)
    contacts = repository.list_all()

    assert len(contacts) == 0


def test_find_by_name_no_results(repository):
    """Test searching with no matches returns empty list."""
    results = repository.find_by_name("NonExistent")

    assert results == []


def test_find_by_email_no_results(repository):
    """Test finding by email with no match returns None."""
    found = repository.find_by_email("nobody@example.com")

    assert found is None


def test_add_duplicate_email_raises_app_error(repository):
    """Duplicate email should raise a user-correctable error."""
    contact_a = Contact.create(
        first_name="Ana",
        last_name="Lopez",
        email="dup@example.com",
        phone="111-111-1111",
    )
    contact_b = Contact.create(
        first_name="Bob",
        last_name="Smith",
        email="dup@example.com",
        phone="222-222-2222",
    )
    repository.add(contact_a)

    with pytest.raises(AppError) as exc:
        repository.add(contact_b)

    assert exc.value.code == "DUPLICATE_EMAIL"


def test_update_duplicate_email_raises_app_error(repository):
    """Updating to an existing email should raise a user-correctable error."""
    contact_a = Contact.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana@example.com",
        phone="111-111-1111",
    )
    contact_b = Contact.create(
        first_name="Bob",
        last_name="Smith",
        email="bob@example.com",
        phone="222-222-2222",
    )
    saved_a = repository.add(contact_a)
    saved_b = repository.add(contact_b)
    saved_b.email = saved_a.email

    with pytest.raises(AppError) as exc:
        repository.update(saved_b)

    assert exc.value.code == "DUPLICATE_EMAIL"
