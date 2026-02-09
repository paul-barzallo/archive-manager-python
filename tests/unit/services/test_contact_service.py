#!/usr/bin/env python3
"""Unit tests for ContactService business logic."""

from __future__ import annotations

import pytest

from archive_manager.core.errors import AppValidationErrors, AppWarning


def _error_codes(exc: AppValidationErrors) -> list[str]:
    """Extract error codes from AppValidationErrors exception."""
    return [err.code for err in exc.errors]


def test_create_contact_happy_path(service) -> None:
    """Test successful contact creation."""
    contact = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    assert contact.contact_id == 1
    assert service.list_all() == [contact]


def test_create_contact_duplicate_email(service) -> None:
    """Test that duplicate email raises validation error."""
    service.create("Ana", "Lopez", "ana@example.com", "600000000")
    with pytest.raises(AppValidationErrors) as ei:
        service.create("Bob", "Doe", "ana@example.com", "700000000")
    assert "DUPLICATE_EMAIL" in _error_codes(ei.value)


def test_create_contact_duplicate_phone(service) -> None:
    """Test that duplicate phone raises validation error."""
    service.create("Ana", "Lopez", "ana@example.com", "600000000")
    with pytest.raises(AppValidationErrors) as ei:
        service.create("Bob", "Doe", "bob@example.com", "600000000")
    assert "DUPLICATE_PHONE" in _error_codes(ei.value)


def test_find_by_name_requires_one_field(service) -> None:
    """Test that find_by_name requires non-empty input."""
    with pytest.raises(AppValidationErrors) as ei:
        service.find_by_name("")
    assert "FIRST_OR_LAST_REQUIRED" in _error_codes(ei.value)


def test_find_by_name_returns_matches(service) -> None:
    """Test that find_by_name returns matching contacts."""
    ana = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    bob = service.create("Bob", "Smith", "bob@example.com", "700000000")
    results = service.find_by_name("ana")
    assert ana in results
    assert bob not in results


def test_find_by_name_matches_last_name(service) -> None:
    """Test that find_by_name matches last name substrings."""
    ana = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    results = service.find_by_name("pez")
    assert ana in results


def test_find_by_name_matches_full_name_substring(service) -> None:
    """Test that find_by_name matches full name substrings."""
    ana = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    results = service.find_by_name("ana lo")
    assert ana in results


def test_find_by_email_not_found(service) -> None:
    """Test that find_by_email raises warning when not found."""
    with pytest.raises(AppWarning) as wi:
        service.find_by_email("missing@example.com")
    assert wi.value.code == "CONTACT_NOT_FOUND"


def test_find_by_phone_not_found(service) -> None:
    """Test that find_by_phone raises warning when not found."""
    with pytest.raises(AppWarning) as wi:
        service.find_by_phone("600000000")
    assert wi.value.code == "CONTACT_NOT_FOUND"


def test_list_all_empty_warns(service) -> None:
    """Test that list_all raises warning when empty."""
    with pytest.raises(AppWarning) as wi:
        service.list_all()
    assert wi.value.code == "EMPTY_CONTACT_LIST"


def test_list_contacts_empty_warns(service) -> None:
    """Test that paginated list raises warning when empty."""
    with pytest.raises(AppWarning) as wi:
        service.list_contacts()
    assert wi.value.code == "EMPTY_CONTACT_LIST"


def test_list_contacts_returns_paginated_page(service) -> None:
    """Test paginated list returns page metadata and sliced results."""
    for i in range(3):
        service.create("Name", "User", f"user{i}@example.com", f"60000000{i}")

    page = service.list_contacts(limit=2, offset=1)

    assert page.total == 3
    assert page.limit == 2
    assert page.offset == 1
    assert len(page.contacts) == 2
    assert page.contacts[0].email == "user1@example.com"
    assert page.contacts[1].email == "user2@example.com"


def test_list_contacts_clamps_limit_to_max(service) -> None:
    """Test list_contacts enforces max limit of 20 results."""
    for i in range(25):
        service.create("Name", "User", f"user{i}@example.com", f"7000000{i:02d}")

    page = service.list_contacts(limit=100)

    assert page.total == 25
    assert page.limit == 20
    assert len(page.contacts) == 20


def test_update_contact_prevents_duplicate_email(service) -> None:
    """Test that update prevents duplicate email."""
    ana = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    bob = service.create("Bob", "Smith", "bob@example.com", "700000000")
    with pytest.raises(AppValidationErrors) as ei:
        service.update(
            ana.contact_id,
            ana.first_name,
            ana.last_name,
            bob.email,
            ana.phone,
        )
    assert "DUPLICATE_EMAIL" in _error_codes(ei.value)


def test_update_contact_prevents_duplicate_phone(service) -> None:
    """Test that update prevents duplicate phone."""
    ana = service.create("Ana", "Lopez", "ana@example.com", "600000000")
    bob = service.create("Bob", "Smith", "bob@example.com", "700000000")
    with pytest.raises(AppValidationErrors) as ei:
        service.update(
            ana.contact_id,
            ana.first_name,
            ana.last_name,
            ana.email,
            bob.phone,
        )
    assert "DUPLICATE_PHONE" in _error_codes(ei.value)


def test_delete_contact_not_found_logs_warning(service) -> None:
    """Test that delete of non-existent contact completes without error.

    The repository logs a warning but doesn't raise an exception,
    as it's an idempotent operation.
    """
    # Should not raise - idempotent delete
    service.delete(99)
