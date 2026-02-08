#!/usr/bin/env python3
"""Unit tests for ContactValidator.

Tests cover:
- Required vs optional field validation
- Valid input handling
- Format validation (email, phone, names)
- Edge cases (boundary lengths, special characters)
- Security considerations
"""

from __future__ import annotations

import pytest

from archive_manager.core.entities.validators import ContactValidator

# ==============================================================================
# First Name Validation Tests
# ==============================================================================


class TestFirstNameValidation:
    """Tests for first name validation."""

    @pytest.mark.parametrize(
        ("name", "expected_code"),
        [
            ("", "FIRST_NAME_REQUIRED"),  # Empty required
            ("a" * 101, "MAX_NAME_LENGTH"),  # Too long
            ("john123", "INVALID_FIRST_NAME"),  # Numbers
            ("<script>", "INVALID_FIRST_NAME"),  # Special chars
        ],
    )
    def test_first_name_invalids_fails(self, name, expected_code):
        """Test invalid first names fail validation."""
        validator = ContactValidator()
        validator.validate_first_name(name, required=True)

        assert expected_code in [err.code for err in validator.errors]

    @pytest.mark.parametrize(
        "name",
        [
            "",  # Optional empty
            "maria",  # Standard
            "josé",  # Accents
            "mary-jane",  # Hyphen
            "a" * 100,  # Max length
        ],
    )
    def test_first_name_valid_succeeds(self, name):
        """Test valid first names succeed."""
        validator = ContactValidator()
        result = validator.validate_first_name(name, required=False)

        assert result == name
        assert validator.errors == []


# ==============================================================================
# Last Name Validation Tests
# ==============================================================================


class TestLastNameValidation:
    """Tests for last name validation."""

    def test_last_name_required_empty_fails(self):
        """Empty last name fails when required."""
        validator = ContactValidator()
        validator.validate_last_name("", required=True)

        assert [err.code for err in validator.errors] == ["LAST_NAME_REQUIRED"]

    def test_last_name_optional_empty_succeeds(self):
        """Empty last name succeeds when optional."""
        validator = ContactValidator()
        result = validator.validate_last_name("", required=False)

        assert result == ""
        assert validator.errors == []

    def test_last_name_with_apostrophe(self):
        """Last name with apostrophe is valid."""
        validator = ContactValidator()
        result = validator.validate_last_name("o'brien")

        assert result == "o'brien"
        assert validator.errors == []

    def test_last_name_with_space(self):
        """Last name with space is valid."""
        validator = ContactValidator()
        result = validator.validate_last_name("van der berg")

        assert result == "van der berg"
        assert validator.errors == []


# ==============================================================================
# Email Validation Tests
# ==============================================================================


class TestEmailValidation:
    """Tests for email validation."""

    def test_email_required_empty_fails(self):
        """Empty email fails when required."""
        validator = ContactValidator()
        validator.validate_email("", required=True)

        assert [err.code for err in validator.errors] == ["EMAIL_REQUIRED"]

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",  # Standard
            "user@mail.example.com",  # Subdomain
            "user+tag@example.com",  # Plus sign
        ],
    )
    def test_email_valid_format(self, email):
        """Valid email format is accepted."""
        validator = ContactValidator()
        result = validator.validate_email(email)

        assert result == email
        assert validator.errors == []

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "not-an-email",  # Invalid format
            "userexample.com",  # Missing @
            "user@",  # Missing domain
            "user@example",  # Missing TLD
        ],
    )
    def test_email_invalid_format(self, invalid_email):
        """Invalid email format fails validation."""
        validator = ContactValidator()
        validator.validate_email(invalid_email)

        assert [err.code for err in validator.errors] == ["INVALID_EMAIL"]


# ==============================================================================
# Phone Validation Tests
# ==============================================================================


class TestPhoneValidation:
    """Tests for phone validation per ITU-T E.164."""

    def test_phone_optional_empty_succeeds(self):
        """Empty phone succeeds when optional."""
        validator = ContactValidator()
        result = validator.validate_phone("", required=False)

        assert result == ""
        assert validator.errors == []

    def test_phone_required_empty_fails(self):
        """Empty phone fails when required."""
        validator = ContactValidator()
        validator.validate_phone("", required=True)

        assert [err.code for err in validator.errors] == ["PHONE_REQUIRED"]

    def test_phone_too_short(self):
        """Phone with fewer than 7 digits fails E.164 minimum."""
        validator = ContactValidator()
        validator.validate_phone("12345", required=True)

        assert [err.code for err in validator.errors] == ["MIN_PHONE_DIGITS"]

    def test_phone_minimum_digits(self):
        """Phone with exactly 7 digits passes E.164 minimum."""
        validator = ContactValidator()
        result = validator.validate_phone("1234567")

        assert result == "1234567"
        assert validator.errors == []

    def test_phone_maximum_digits(self):
        """Phone with exactly 15 digits passes E.164 maximum."""
        validator = ContactValidator()
        result = validator.validate_phone("+123456789012345")

        assert result == "+123456789012345"
        assert validator.errors == []

    def test_phone_exceeds_maximum_digits(self):
        """Phone with more than 15 digits fails E.164 maximum."""
        validator = ContactValidator()
        validator.validate_phone("+1234567890123456")

        assert [err.code for err in validator.errors] == ["MAX_PHONE_DIGITS"]

    def test_phone_with_international_format(self):
        """Phone with E.164 international format is valid."""
        validator = ContactValidator()
        result = validator.validate_phone("+34 600 000 000")

        assert result == "+34 600 000 000"
        assert validator.errors == []

    def test_phone_with_parentheses(self):
        """Phone with parentheses format is valid."""
        validator = ContactValidator()
        result = validator.validate_phone("(555) 123-4567")

        assert result == "(555) 123-4567"
        assert validator.errors == []

    def test_phone_with_letters_fails(self):
        """Phone with letters fails validation."""
        validator = ContactValidator()
        validator.validate_phone("555-CALL")

        error_codes = [err.code for err in validator.errors]
        assert "INVALID_PHONE" in error_codes


# ==============================================================================
# Security Tests
# ==============================================================================


@pytest.mark.security
class TestValidatorSecurity:
    """Security-focused validation tests."""

    def test_sql_injection_in_name_fails(self):
        """SQL injection attempt in name fails validation."""
        validator = ContactValidator()
        validator.validate_first_name("'; DROP TABLE contacts; --")

        assert "INVALID_FIRST_NAME" in [err.code for err in validator.errors]

    def test_xss_in_name_fails(self):
        """XSS attempt in name fails validation."""
        validator = ContactValidator()
        validator.validate_first_name("<img src=x onerror=alert(1)>")

        assert "INVALID_FIRST_NAME" in [err.code for err in validator.errors]

    def test_script_tag_in_email_local_part(self):
        """Script tag in email local part is rejected."""
        validator = ContactValidator()
        # The email regex rejects angle brackets < > in local part
        validator.validate_email("<script>@example.com")

        # Must fail validation - angle brackets are not valid email characters
        assert "INVALID_EMAIL" in [err.code for err in validator.errors]


# ==============================================================================
# Multiple Errors Tests
# ==============================================================================


class TestMultipleValidationErrors:
    """Tests for collecting multiple validation errors."""

    def test_multiple_errors_accumulated(self):
        """Multiple validation errors are accumulated in single validator."""
        validator = ContactValidator()

        validator.validate_first_name("", required=True)
        validator.validate_last_name("", required=True)
        validator.validate_email("", required=True)

        assert len(validator.errors) == 3
        codes = [err.code for err in validator.errors]
        assert "FIRST_NAME_REQUIRED" in codes
        assert "LAST_NAME_REQUIRED" in codes
        assert "EMAIL_REQUIRED" in codes

    def test_errors_preserved_across_validations(self):
        """Errors from earlier validations are preserved."""
        validator = ContactValidator()

        validator.validate_first_name("123invalid")  # Invalid
        validator.validate_last_name("smith")  # Valid

        assert len(validator.errors) == 1
        assert validator.errors[0].code == "INVALID_FIRST_NAME"
