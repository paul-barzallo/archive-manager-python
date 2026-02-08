#!/usr/bin/env python3
"""Validation utilities for contact data.

Centralizes validation logic and regex patterns to avoid code duplication
across entity, service, and repository layers.
"""

from __future__ import annotations

import re

from archive_manager.core.errors import AppError


class ContactValidator:
    """Instance-based validator for contact fields.

    Collects validation errors in an ``errors`` list for batch processing.
    """

    # Regex constants
    NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")
    # Email: local part allows alphanumeric, dots, hyphens, underscores, plus
    # Explicitly rejects: <, >, quotes, semicolons, and other special chars
    EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^[0-9+() \-]+$")

    # Length limits
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 254
    # ITU-T E.164: phone numbers have 7-15 digits (excluding leading '+')
    MIN_PHONE_DIGITS = 7
    MAX_PHONE_DIGITS = 15

    def __init__(self) -> None:
        """Initialize validator instance."""
        self.errors: list[AppError] = []

    # --- Field validators ---

    def validate_first_name(self, value: str, required: bool = False) -> str:
        """Validate first name.

        Appends errors to ``self.errors`` if validation fails.

        Args:
            value: First name to validate.
            required: Whether the field is required.

        Returns:
            The input value (unchanged).
        """
        if not value:
            if required:
                self.errors.append(
                    AppError(
                        code="FIRST_NAME_REQUIRED",
                        origin="ContactValidator.validate_first_name",
                        field="first_name",
                    )
                )
            return value

        if len(value) > ContactValidator.MAX_NAME_LENGTH:
            self.errors.append(
                AppError(
                    code="MAX_NAME_LENGTH",
                    origin="ContactValidator.validate_first_name",
                    field="first_name",
                    name=value,
                )
            )

        if len(value) < ContactValidator.MIN_NAME_LENGTH:
            self.errors.append(
                AppError(
                    code="MIN_NAME_LENGTH",
                    origin="ContactValidator.validate_first_name",
                    field="first_name",
                    name=value,
                )
            )

        if not ContactValidator.NAME_PATTERN.match(value):
            self.errors.append(
                AppError(
                    code="INVALID_FIRST_NAME",
                    origin="ContactValidator.validate_first_name",
                    field="first_name",
                    name=value,
                )
            )

        return value

    def validate_last_name(self, value: str, required: bool = False) -> str:
        """Validate last name.

        Appends errors to ``self.errors`` if validation fails.

        Args:
            value: Last name to validate.
            required: Whether the field is required.

        Returns:
            The input value (unchanged).
        """
        if not value:
            if required:
                self.errors.append(
                    AppError(
                        code="LAST_NAME_REQUIRED",
                        origin="ContactValidator.validate_last_name",
                        field="last_name",
                    )
                )
            return value

        if len(value) > ContactValidator.MAX_NAME_LENGTH:
            self.errors.append(
                AppError(
                    code="MAX_LAST_NAME_LENGTH",
                    origin="ContactValidator.validate_last_name",
                    field="last_name",
                    name=value,
                )
            )

        if len(value) < ContactValidator.MIN_NAME_LENGTH:
            self.errors.append(
                AppError(
                    code="MIN_LAST_NAME_LENGTH",
                    origin="ContactValidator.validate_last_name",
                    field="last_name",
                    name=value,
                )
            )

        if not ContactValidator.NAME_PATTERN.match(value):
            self.errors.append(
                AppError(
                    code="INVALID_LAST_NAME",
                    origin="ContactValidator.validate_last_name",
                    field="last_name",
                    name=value,
                )
            )
        return value

    def validate_full_name(self, value: str, required: bool = False) -> str:
        """Validate full name (first + last combined).

        Appends errors to ``self.errors`` if validation fails.

        Args:
            value: Full name to validate.
            required: Whether the field is required.

        Returns:
            The input value (unchanged).
        """
        if not value:
            if required:
                self.errors.append(
                    AppError(
                        code="FIRST_OR_LAST_REQUIRED",
                        origin="ContactValidator.validate_full_name",
                        field="full_name",
                    )
                )
            return value

        if len(value) > ContactValidator.MAX_NAME_LENGTH * 2 + 1:  # including space
            self.errors.append(
                AppError(
                    code="MAX_NAME_LENGTH",
                    origin="ContactValidator.validate_full_name",
                    field="full_name",
                    name=value,
                )
            )

        if not ContactValidator.NAME_PATTERN.match(value):
            self.errors.append(
                AppError(
                    code="INVALID_FULL_NAME",
                    origin="ContactValidator.validate_full_name",
                    field="full_name",
                    name=value,
                )
            )
        return value

    def validate_email(self, value: str, required: bool = False) -> str:
        """Validate email address.

        Appends errors to ``self.errors`` if validation fails.

        Args:
            value: Email to validate.
            required: Whether the field is required.

        Returns:
            The input value (unchanged).
        """
        if not value:
            if required:
                self.errors.append(
                    AppError(
                        code="EMAIL_REQUIRED",
                        origin="ContactValidator.validate_email",
                        field="email",
                    )
                )
            return value

        if len(value) > ContactValidator.MAX_EMAIL_LENGTH:
            self.errors.append(
                AppError(
                    code="MAX_EMAIL_LENGTH",
                    origin="ContactValidator.validate_email",
                    field="email",
                    email=value,
                )
            )
        if not ContactValidator.EMAIL_PATTERN.match(value):
            self.errors.append(
                AppError(
                    code="INVALID_EMAIL",
                    origin="ContactValidator.validate_email",
                    field="email",
                    email=value,
                )
            )

        return value

    def validate_phone(self, value: str, required: bool = False) -> str:
        """Validate phone number format per ITU-T E.164.

        E.164 defines a maximum of 15 digits and a minimum of 7 digits
        (excluding the optional leading ``+``). The validator checks
        digit count and allowed characters (digits, ``+``, spaces,
        dashes, parentheses).

        Appends errors to ``self.errors`` if validation fails.

        Args:
            value: Phone to validate (raw format before canonicalization).
            required: Whether the field is required.

        Returns:
            The input value (unchanged).
        """
        if not value:
            if required:
                self.errors.append(
                    AppError(
                        code="PHONE_REQUIRED",
                        origin="ContactValidator.validate_phone",
                        field="phone",
                    )
                )
            return value

        # Count digits only (E.164 limits exclude the leading '+')
        digits = re.sub(r"\D", "", value)
        if len(digits) < ContactValidator.MIN_PHONE_DIGITS:
            self.errors.append(
                AppError(
                    code="MIN_PHONE_DIGITS",
                    origin="ContactValidator.validate_phone",
                    field="phone",
                    phone=value,
                )
            )

        if len(digits) > ContactValidator.MAX_PHONE_DIGITS:
            self.errors.append(
                AppError(
                    code="MAX_PHONE_DIGITS",
                    origin="ContactValidator.validate_phone",
                    field="phone",
                    phone=value,
                )
            )

        if not ContactValidator.PHONE_PATTERN.match(value):
            self.errors.append(
                AppError(
                    code="INVALID_PHONE",
                    origin="ContactValidator.validate_phone",
                    field="phone",
                    phone=value,
                )
            )

        return value

    # --- Static normalization / canonicalization methods ---

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize a name by stripping, lowercasing, and collapsing whitespace.

        Args:
            name: Name string to normalize.

        Returns:
            Normalized name with single spaces between words.
        """
        return " ".join(name.strip().lower().split())

    @staticmethod
    def normalize_string(value: str) -> str:
        """Normalize a string by stripping and lowercasing.

        Args:
            value: String to normalize.

        Returns:
            Normalized string.
        """
        return value.strip().lower()

    @staticmethod
    def canonicalize_phone(phone: str) -> str:
        """Convert phone to E.164 canonical format for storage and comparison.

        Keeps the leading ``+`` (if present) and digits only, stripping all
        other characters (spaces, dashes, parentheses). The result conforms
        to ITU-T E.164: optional ``+`` prefix followed by 7-15 digits.

        Examples:
            - ``"+34 600 000 000"`` → ``"+34600000000"``
            - ``"(555) 123-4567"`` → ``"5551234567"``
            - ``""`` → ``""``

        Args:
            phone: Phone string to canonicalize.

        Returns:
            Canonical phone string (``+`` prefix + digits, or digits only).
        """
        if not phone:
            return ""
        stripped = phone.strip()
        if not stripped:
            return ""
        prefix = "+" if stripped.startswith("+") else ""
        digits = re.sub(r"\D", "", stripped)
        return prefix + digits if digits else ""
