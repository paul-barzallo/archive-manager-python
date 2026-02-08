#!/usr/bin/env python3
"""Unit tests for Contact entity.

Tests cover:
- Valid contact creation
- Validation error handling
- Edge cases with special characters
- Boundary conditions (min/max lengths)
- Equality and representation
"""

from __future__ import annotations

import pytest

from archive_manager.core.entities import Contact
from archive_manager.core.errors import AppValidationErrors

# ==============================================================================
# Basic Creation Tests
# ==============================================================================


class TestContactCreation:
    """Tests for contact creation and basic operations."""

    def test_contact_valid_creation_and_repr(self):
        """Test creating a valid contact and its Python representation."""
        contact = Contact.create(
            contact_id=1,
            first_name="ana",
            last_name="lopez",
            phone="+34 600 000 000",
            email="ana@example.com",
        )
        repr_str = repr(contact)

        # Verify repr format is Python-style (not JSON)
        assert repr_str.startswith("Contact(")
        assert repr_str.endswith(")")
        assert "contact_id=1" in repr_str
        assert "first_name='ana'" in repr_str
        assert "last_name='lopez'" in repr_str
        assert "email='ana@example.com'" in repr_str
        assert "phone='+34600000000'" in repr_str

    def test_contact_creation_without_phone(self):
        """Test creating a valid contact without phone number."""
        contact = Contact.create(
            contact_id=0,
            first_name="john",
            last_name="doe",
            phone="",
            email="john@example.com",
        )

        assert contact.first_name == "john"
        assert contact.phone == ""

    def test_contact_from_persistence_skips_validation(self):
        """Test that from_persistence creates contact without validation."""
        # This would fail validation if validated (empty email)
        # but from_persistence should skip validation
        contact = Contact.from_persistence(
            contact_id=1,
            first_name="john",
            last_name="doe",
            phone="",
            email="john@example.com",
        )

        assert contact.contact_id == 1
        assert contact.first_name == "john"

    def test_contact_equality_by_id(self):
        """Test that contacts are equal if they have the same ID."""
        a = Contact.create(
            contact_id=1,
            first_name="ana",
            last_name="lopez",
            phone="",
            email="ana@example.com",
        )
        b = Contact.create(
            contact_id=1,
            first_name="ana",
            last_name="lopez",
            phone="",
            email="ana@example.com",
        )

        assert a == b

    def test_contact_inequality_different_ids(self):
        """Test that contacts with different IDs are not equal."""
        a = Contact.create(
            contact_id=1,
            first_name="ana",
            last_name="lopez",
            phone="",
            email="ana@example.com",
        )
        b = Contact.create(
            contact_id=2,
            first_name="ana",
            last_name="lopez",
            phone="",
            email="ana2@example.com",
        )

        assert a != b

    def test_contact_not_equal_to_non_contact(self):
        """Test that contact is not equal to non-Contact objects."""
        contact = Contact.create(
            contact_id=1,
            first_name="ana",
            last_name="lopez",
            phone="",
            email="ana@example.com",
        )

        assert contact != "not a contact"
        assert contact != 1
        assert contact != None  # noqa: E711

    def test_direct_instantiation_raises_type_error(self):
        """Test that direct __init__ call raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            Contact()

        assert "Contact.create()" in str(exc_info.value)
        assert "Contact.from_persistence()" in str(exc_info.value)


# ==============================================================================
# Validation Error Tests
# ==============================================================================


class TestContactValidation:
    """Tests for contact validation error handling."""

    def test_contact_empty_first_name_raises(self):
        """Test that empty first name raises AppValidationErrors."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="",
                last_name="doe",
                phone="",
                email="john@example.com",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "FIRST_NAME_REQUIRED" in error_codes

    def test_contact_empty_last_name_raises(self):
        """Test that empty last name raises AppValidationErrors."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="john",
                last_name="",
                phone="",
                email="john@example.com",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "LAST_NAME_REQUIRED" in error_codes

    def test_contact_empty_email_raises(self):
        """Test that empty email raises AppValidationErrors."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="john",
                last_name="doe",
                phone="",
                email="",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "EMAIL_REQUIRED" in error_codes

    def test_contact_invalid_email_raises(self):
        """Test that invalid email format raises AppValidationErrors."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="john",
                last_name="doe",
                phone="",
                email="not-an-email",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "INVALID_EMAIL" in error_codes

    def test_contact_multiple_validation_errors(self):
        """Test that multiple validation errors are collected."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="",
                last_name="",
                phone="",
                email="invalid",
            )

        # Should have at least 3 errors (first_name, last_name, email)
        assert len(exc_info.value.errors) >= 3

    def test_contact_invalid_phone_too_few_digits(self):
        """Test that phone with too few digits raises AppValidationErrors."""
        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name="john",
                last_name="doe",
                phone="123",  # Only 3 digits
                email="john@example.com",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "MIN_PHONE_DIGITS" in error_codes


# ==============================================================================
# Special Characters Tests
# ==============================================================================


class TestContactSpecialCharacters:
    """Tests for contacts with special characters in names."""

    @pytest.mark.parametrize(
        ("first_name", "last_name"),
        [
            ("josé", "garcía"),  # Spanish accents
            ("françois", "lemaître"),  # French accents
            ("müller", "schröder"),  # German umlauts
            ("marie-claire", "jones"),  # Hyphen
            ("mary", "o'brien"),  # Apostrophe
        ],
    )
    def test_contact_with_special_characters(self, first_name, last_name):
        """Test creating contact with various special characters."""
        contact = Contact.create(
            contact_id=0,
            first_name=first_name,
            last_name=last_name,
            phone="",
            email="test@example.com",
        )
        assert contact.first_name == first_name
        assert contact.last_name == last_name

    def test_contact_with_international_phone(self):
        """Test creating contact with international phone format."""
        contact = Contact.create(
            contact_id=0,
            first_name="john",
            last_name="doe",
            phone="+34 600 000 000",
            email="john@example.com",
        )

        assert contact.phone == "+34600000000"


# ==============================================================================
# Boundary Condition Tests
# ==============================================================================


class TestContactBoundaries:
    """Tests for boundary conditions (min/max lengths)."""

    def test_contact_with_max_name_length(self):
        """Test creating contact with maximum length name (100 chars)."""
        long_name = "a" * 100
        contact = Contact.create(
            contact_id=0,
            first_name=long_name,
            last_name=long_name,
            phone="",
            email="test@example.com",
        )

        assert len(contact.first_name) == 100
        assert len(contact.last_name) == 100

    def test_contact_name_exceeds_max_length(self):
        """Test that name exceeding max length raises AppValidationErrors."""
        too_long_name = "a" * 101  # Max is 100

        with pytest.raises(AppValidationErrors) as exc_info:
            Contact.create(
                contact_id=0,
                first_name=too_long_name,
                last_name="doe",
                phone="",
                email="test@example.com",
            )

        error_codes = [e.code for e in exc_info.value.errors]
        assert "MAX_NAME_LENGTH" in error_codes

    def test_contact_with_min_valid_phone(self):
        """Test creating contact with minimum valid phone (7 digits)."""
        contact = Contact.create(
            contact_id=0,
            first_name="john",
            last_name="doe",
            phone="1234567",
            email="john@example.com",
        )

        assert contact.phone == "1234567"

    def test_contact_with_max_email_length(self):
        """Test creating contact with near-maximum email length."""
        # Max email is 254 characters
        local_part = "a" * 240
        email = f"{local_part}@example.com"

        contact = Contact.create(
            contact_id=0,
            first_name="john",
            last_name="doe",
            phone="",
            email=email,
        )

        assert contact.email == email


# ==============================================================================
# Security Tests
# ==============================================================================


@pytest.mark.security
class TestContactSecurityInputs:
    """Tests for potentially malicious inputs (SQL injection, XSS, etc.)."""

    @pytest.mark.parametrize(
        "invalid_name",
        ["12345", "<script>", "john;drop", 'john"test'],
    )
    def test_contact_rejects_invalid_names(self, invalid_name):
        """Test that invalid/malicious names are rejected."""
        with pytest.raises(AppValidationErrors):
            Contact.create(
                contact_id=0,
                first_name=invalid_name,
                last_name="doe",
                phone="",
                email="test@example.com",
            )
