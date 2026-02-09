#!/usr/bin/env python3
"""Integration tests for the complete contact management flow.

These tests verify the full stack from Controller -> Service -> Repository -> Database,
ensuring all layers work together correctly.

Note on logging language:
    All log/test messages are in English for consistency with internal systems.
    Internationalization is only for user-facing presentation.
"""

from __future__ import annotations

from contextlib import suppress

import pytest

from archive_manager.adapters.cli import ContactCslController
from archive_manager.application.dto import ContactDTO
from archive_manager.application.services import ContactService
from archive_manager.core.errors import AppValidationErrors, AppWarning
from archive_manager.infrastructure.persistence import SqliteContactRepository
from archive_manager.infrastructure.persistence.db import SqliteConnection

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def integration_stack():
    """Create a full integration stack with all layers connected.

    Returns a tuple of (controller, service, repository, connection).
    """
    db = SqliteConnection("sqlite:///:memory:")
    repo = SqliteContactRepository(db)
    svc = ContactService(repository=repo)
    ctrl = ContactCslController(service=svc)

    yield ctrl, svc, repo, db

    db.close()


# ==============================================================================
# Happy Path Integration Tests
# ==============================================================================


@pytest.mark.integration
class TestContactCreationFlow:
    """Integration tests for contact creation end-to-end."""

    def test_create_contact_full_stack(self, integration_stack):
        """Test creating a contact through all layers."""
        ctrl, _svc, repo, _ = integration_stack

        # Create via controller (simulates UI action)
        dto = ContactDTO(
            contact_id=0,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
        )
        result = ctrl.add_contact(dto)

        # Verify result
        assert result.contact_id > 0
        assert result.first_name == "John"  # Title Case via ContactDTO.from_entity()
        assert result.email == "john@example.com"

        # Verify persisted in database
        persisted = repo.find_by_email("john@example.com")
        assert persisted is not None
        assert persisted.contact_id == result.contact_id

    def test_create_and_list_multiple_contacts(self, integration_stack):
        """Test creating multiple contacts and listing them."""
        ctrl, _, _, _ = integration_stack

        contacts_data = [
            ("Ana", "López", "ana@example.com", "1111111111"),
            ("Bob", "Smith", "bob@example.com", "2222222222"),
            ("Carlos", "García", "carlos@example.com", "3333333333"),
        ]

        for first, last, email, phone in contacts_data:
            dto = ContactDTO(0, first, last, email, phone)
            ctrl.add_contact(dto)

        # List all contacts
        page = ctrl.list_contacts()

        assert len(page.contacts) == 3
        emails = {c.email for c in page.contacts}
        assert emails == {"ana@example.com", "bob@example.com", "carlos@example.com"}

    def test_list_contacts_uses_default_limit_and_offset(self, integration_stack):
        """Test controller exposes page counters and item ranges."""
        ctrl, _, _, _ = integration_stack

        for i in range(52):
            ctrl.add_contact(
                ContactDTO(
                    0,
                    "Name",
                    "User",
                    f"user{i}@example.com",
                    f"6{i + 1000000000}",
                )
            )

        first_page = ctrl.list_contacts()
        second_page = ctrl.list_contacts(offset=20)
        third_page = ctrl.list_contacts(offset=40)

        assert first_page.total == 52
        assert first_page.limit == 20
        assert first_page.offset == 0
        assert first_page.shown == 20
        assert first_page.current_page == 1
        assert first_page.total_pages == 3
        assert first_page.start_item == 1
        assert first_page.end_item == 20
        assert first_page.has_next is True
        assert first_page.has_previous is False

        assert second_page.total == 52
        assert second_page.limit == 20
        assert second_page.offset == 20
        assert second_page.shown == 20
        assert second_page.current_page == 2
        assert second_page.total_pages == 3
        assert second_page.start_item == 21
        assert second_page.end_item == 40
        assert second_page.has_next is True
        assert second_page.has_previous is True

        assert third_page.total == 52
        assert third_page.limit == 20
        assert third_page.offset == 40
        assert third_page.shown == 12
        assert third_page.current_page == 3
        assert third_page.total_pages == 3
        assert third_page.start_item == 41
        assert third_page.end_item == 52
        assert third_page.has_next is False
        assert third_page.has_previous is True


@pytest.mark.integration
class TestContactSearchFlow:
    """Integration tests for contact search functionality."""

    def test_search_by_name_partial_match(self, integration_stack):
        """Test searching contacts by partial name match."""
        ctrl, _, _, _ = integration_stack

        # Create contacts
        ctrl.add_contact(ContactDTO(0, "John", "Doe", "john@example.com", "1111111111"))
        ctrl.add_contact(ContactDTO(0, "Jane", "Doe", "jane@example.com", "2222222222"))
        ctrl.add_contact(ContactDTO(0, "Bob", "Smith", "bob@example.com", "3333333333"))

        # Search by last name
        results = ctrl.search_contact_by_name("doe")

        assert len(results) == 2
        first_names = {c.first_name for c in results}
        assert first_names == {"John", "Jane"}

    def test_search_by_email_exact_match(self, integration_stack):
        """Test searching contact by exact email."""
        ctrl, _, _, _ = integration_stack

        ctrl.add_contact(ContactDTO(0, "John", "Doe", "john@example.com", "1111111111"))

        result = ctrl.search_contact_by_email("john@example.com")

        assert result is not None
        assert result.first_name == "John"

    def test_search_by_phone_exact_match(self, integration_stack):
        """Test searching contact by exact phone number."""
        ctrl, _, _, _ = integration_stack

        ctrl.add_contact(ContactDTO(0, "John", "Doe", "john@example.com", "1234567890"))

        result = ctrl.search_contact_by_phone("1234567890")

        assert result is not None
        assert result.email == "john@example.com"


@pytest.mark.integration
class TestContactUpdateFlow:
    """Integration tests for contact update functionality."""

    def test_update_contact_full_stack(self, integration_stack):
        """Test updating a contact through all layers."""
        ctrl, _, repo, _ = integration_stack

        # Create initial contact
        created = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1111111111")
        )

        # Update contact
        updated_dto = ContactDTO(
            contact_id=created.contact_id,
            first_name="Johnny",
            last_name="Doe",
            email="johnny@example.com",
            phone="9999999999",
        )
        result = ctrl.edit_contact(updated_dto)

        # Verify result (DTO returns Title Case)
        assert result.first_name == "Johnny"
        assert result.email == "johnny@example.com"

        # Verify persisted (entity stores lowercase)
        persisted = repo.find_by_email("johnny@example.com")
        assert persisted is not None
        assert persisted.first_name == "johnny"

        # Old email should not exist
        old = repo.find_by_email("john@example.com")
        assert old is None


@pytest.mark.integration
class TestContactDeleteFlow:
    """Integration tests for contact deletion (soft delete) functionality."""

    def test_soft_delete_contact(self, integration_stack):
        """Test soft deleting a contact."""
        ctrl, _, _repo, _ = integration_stack

        # Create contact
        created = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1111111111")
        )

        # Delete contact
        ctrl.delete_contact(created.contact_id)

        # Contact should not appear in regular queries (empty list raises AppWarning)
        with pytest.raises(AppWarning) as wi:
            ctrl.list_contacts()
        assert wi.value.code == "EMPTY_CONTACT_LIST"

    def test_email_can_be_reused_after_soft_delete(self, integration_stack):
        """Test that email can be reused after contact is soft deleted."""
        ctrl, _svc, _repo, _ = integration_stack

        # Create and delete contact
        created = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1111111111")
        )
        ctrl.delete_contact(created.contact_id)

        # Create new contact with same email
        new_contact = ctrl.add_contact(
            ContactDTO(0, "Jane", "Doe", "john@example.com", "2222222222")
        )

        assert new_contact.contact_id != created.contact_id
        assert new_contact.email == "john@example.com"

    def test_restore_soft_deleted_contact(self, integration_stack):
        """Test restoring a soft deleted contact."""
        ctrl, _, repo, _ = integration_stack

        # Create and delete contact
        created = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1111111111")
        )
        ctrl.delete_contact(created.contact_id)

        # Restore contact
        restored = repo.restore(created.contact_id)

        assert restored.email == "john@example.com"

        # Contact should appear in list again
        page = ctrl.list_contacts()
        assert len(page.contacts) == 1


# ==============================================================================
# Error Handling Integration Tests
# ==============================================================================


@pytest.mark.integration
class TestErrorPropagation:
    """Integration tests for error handling across layers."""

    def test_validation_error_propagates_from_entity(self, integration_stack):
        """Test that validation errors from entity layer propagate correctly."""
        ctrl, _, _, _ = integration_stack

        with pytest.raises(AppValidationErrors) as exc_info:
            ctrl.add_contact(
                ContactDTO(0, "", "", "invalid-email", "123")  # All invalid
            )

        # Should have multiple errors
        assert len(exc_info.value.errors) > 0
        error_codes = [e.code for e in exc_info.value.errors]
        assert "FIRST_NAME_REQUIRED" in error_codes or "INVALID_EMAIL" in error_codes

    def test_duplicate_email_error(self, integration_stack):
        """Test duplicate email error propagates correctly."""
        ctrl, _, _, _ = integration_stack

        # Create first contact
        ctrl.add_contact(ContactDTO(0, "John", "Doe", "john@example.com", "1111111111"))

        # Try to create with same email
        with pytest.raises(AppValidationErrors) as exc_info:
            ctrl.add_contact(
                ContactDTO(0, "Jane", "Doe", "john@example.com", "2222222222")
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "DUPLICATE_EMAIL" in error_codes

    def test_not_found_warning(self, integration_stack):
        """Test not found warning for non-existent contact."""
        ctrl, _, _, _ = integration_stack

        with pytest.raises(AppWarning) as exc_info:
            ctrl.search_contact_by_email("nonexistent@example.com")

        assert exc_info.value.code == "CONTACT_NOT_FOUND"


# ==============================================================================
# Edge Cases and Special Characters
# ==============================================================================


@pytest.mark.integration
class TestSpecialCharacters:
    """Integration tests for contacts with special characters."""

    def test_contact_with_accented_characters(self, integration_stack):
        """Test creating contact with accented characters (Spanish, French, German)."""
        ctrl, _, _, _ = integration_stack

        # Spanish accents
        result = ctrl.add_contact(
            ContactDTO(0, "José", "García Muñoz", "jose@example.com", "1111111111")
        )
        assert result.first_name == "José"

        # German umlaut
        result2 = ctrl.add_contact(
            ContactDTO(0, "Müller", "Schröder", "muller@example.com", "2222222222")
        )
        assert result2.first_name == "Müller"

    def test_contact_with_hyphen_and_apostrophe(self, integration_stack):
        """Test creating contact with hyphenated names and apostrophes."""
        ctrl, _, _, _ = integration_stack

        result = ctrl.add_contact(
            ContactDTO(0, "Marie-Claire", "O'Brien", "marie@example.com", "1111111111")
        )

        assert result.first_name == "Marie-Claire"
        assert result.last_name == "O'Brien"

    def test_search_with_special_characters(self, integration_stack):
        """Test searching with special characters."""
        ctrl, _, _, _ = integration_stack

        ctrl.add_contact(
            ContactDTO(0, "José", "García", "jose@example.com", "1111111111")
        )

        # Search with accent
        results = ctrl.search_contact_by_name("josé")
        assert len(results) == 1

        # Search partial with accent
        results = ctrl.search_contact_by_name("garc")
        assert len(results) == 1


@pytest.mark.integration
class TestEdgeCases:
    """Integration tests for edge cases and boundary conditions."""

    def test_contact_with_max_length_fields(self, integration_stack):
        """Test creating contact with maximum length field values."""
        ctrl, _, _, _ = integration_stack

        long_name = "a" * 100  # Max name length (100 chars)
        long_email = "a" * 240 + "@example.com"  # Close to max email length

        result = ctrl.add_contact(
            ContactDTO(0, long_name, long_name, long_email, "1111111111")
        )

        assert len(result.first_name) == 100
        assert result.email == long_email

    def test_contact_with_minimum_valid_phone(self, integration_stack):
        """Test creating contact with minimum valid phone (7 digits)."""
        ctrl, _, _, _ = integration_stack

        result = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1234567")
        )

        assert result.phone == "1234567"

    def test_contact_with_international_phone_format(self, integration_stack):
        """Test creating contact with various international phone formats."""
        ctrl, _, _, _ = integration_stack

        # International format with plus
        result = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "+34 600 000 000")
        )
        assert result.phone == "+34600000000"

    def test_empty_list_warning(self, integration_stack):
        """Test that empty contact list raises appropriate warning."""
        _ctrl, svc, _, _ = integration_stack

        with pytest.raises(AppWarning) as exc_info:
            svc.list_all()

        assert exc_info.value.code == "EMPTY_CONTACT_LIST"


# ==============================================================================
# Concurrency and Transaction Tests
# ==============================================================================


@pytest.mark.integration
class TestTransactions:
    """Integration tests for transaction handling."""

    def test_failed_create_does_not_persist(self, integration_stack):
        """Test that failed creation doesn't leave partial data."""
        ctrl, _, repo, _ = integration_stack

        # Create a valid contact first
        ctrl.add_contact(ContactDTO(0, "John", "Doe", "john@example.com", "1111111111"))

        # Try to create invalid contact (duplicate email)
        with suppress(AppValidationErrors):
            ctrl.add_contact(
                ContactDTO(0, "Jane", "Doe", "john@example.com", "2222222222")
            )

        # Only one contact should exist
        all_contacts = repo.list_all()
        assert len(all_contacts) == 1

    def test_update_rollback_on_error(self, integration_stack):
        """Test that failed update doesn't corrupt data."""
        ctrl, _, repo, _ = integration_stack

        # Create two contacts
        john = ctrl.add_contact(
            ContactDTO(0, "John", "Doe", "john@example.com", "1111111111")
        )
        ctrl.add_contact(ContactDTO(0, "Jane", "Doe", "jane@example.com", "2222222222"))

        # Try to update John with Jane's email (should fail)
        with suppress(AppValidationErrors):
            ctrl.edit_contact(
                ContactDTO(
                    john.contact_id, "John", "Doe", "jane@example.com", "1111111111"
                )
            )

        # John's email should be unchanged
        john_current = repo.find_by_email("john@example.com")
        assert john_current is not None
        assert john_current.first_name == "john"
