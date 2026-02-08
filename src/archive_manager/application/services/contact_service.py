#!/usr/bin/env python3
"""Business logic for contact management."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from archive_manager.application.services.base_service import BaseService
from archive_manager.application.services.policies import ContactPolicy
from archive_manager.core.entities import Contact
from archive_manager.core.entities.validators import ContactValidator
from archive_manager.core.errors import AppValidationErrors, AppWarning
from archive_manager.core.interfaces import ContactRepository
from archive_manager.infrastructure.config import SERVICES

logger = logging.getLogger(__name__)


class ContactService(BaseService[ContactRepository]):
    """Business logic layer for contact management operations.

    Coordinates between controllers and the data layer, enforcing business
    rules such as duplicate validation and data normalization. Handles
    repository operations and domain-specific error handling.
    """

    NAME = SERVICES.CONTACT

    def create(
        self, first_name: str, last_name: str, email: str, phone: str
    ) -> Contact:
        """Create and persist a new contact after validating no duplicates exist.

        Phone numbers are canonicalized before storage so that different
        formatting of the same number is detected as a duplicate.

        Args:
            first_name: Contact's first name (required).
            last_name: Contact's last name (required).
            email: Contact's email address (required).
            phone: Contact's phone number (optional).

        Returns:
            The created Contact with assigned ID.

        Raises:
            AppValidationErrors: If validation fails or a duplicate is detected.
        """
        # Create contact — entity validates its own data and canonicalises phone
        contact = Contact.create(
            first_name=ContactValidator.normalize_name(first_name),
            last_name=ContactValidator.normalize_name(last_name),
            email=ContactValidator.normalize_string(email),
            phone=phone.strip(),
        )

        # Check business rules
        policy = ContactPolicy()
        contact_found = self._repo.find_by_email(contact.email)
        policy.ensure_unique_email(contact_found)
        if contact.phone:
            contact_found = self._repo.find_by_phone(contact.phone)
            policy.ensure_unique_phone(contact_found)
        if policy.errors:
            logger.debug("Duplicate check failed: %s", [e.code for e in policy.errors])
            raise AppValidationErrors(policy.errors, origin="ContactService.create")

        result = self._repo.add(contact)
        logger.info("Contact created successfully: id=%d", result.contact_id)
        return result

    def find_by_name(self, full_name: str) -> Sequence[Contact]:
        """Search contacts by full name (case-insensitive, partial match).

        Args:
            full_name: Full name or partial name to search for.

        Returns:
            List of matching contacts.

        Raises:
            AppValidationErrors: If name is empty or invalid.
            AppWarning: If no matches are found.
        """
        validator = ContactValidator()
        fn = validator.validate_full_name(
            ContactValidator.normalize_name(full_name), required=True
        )
        if validator.errors:
            raise AppValidationErrors(
                validator.errors, origin="ContactService.find_by_name"
            )

        results = self._repo.find_by_name(fn)
        if not results:
            raise AppWarning(
                code="CONTACT_NOT_FOUND",
                origin="ContactService.find_by_name",
                search_field="full_name",
                name=full_name,
            )
        return results

    def find_by_email(self, email: str) -> Contact:
        """Find contact by exact email match (normalized to lowercase).

        Args:
            email: Email address to search.

        Returns:
            Matching Contact.

        Raises:
            AppValidationErrors: If email is invalid.
            AppWarning: If contact does not exist.
        """
        validator = ContactValidator()
        e = validator.validate_email(
            ContactValidator.normalize_string(email), required=True
        )
        if validator.errors:
            raise AppValidationErrors(
                validator.errors, origin="ContactService.find_by_email"
            )

        result = self._repo.find_by_email(e)
        if not result:
            raise AppWarning(
                code="CONTACT_NOT_FOUND",
                origin="ContactService.find_by_email",
                search_field="email",
                email=email,
            )
        return result

    def find_by_phone(self, phone: str) -> Contact:
        """Find contact by exact phone match (canonicalized).

        The search input is canonicalized to match stored canonical phones.

        Args:
            phone: Phone number to search.

        Returns:
            Matching Contact.

        Raises:
            AppValidationErrors: If phone is invalid.
            AppWarning: If contact does not exist.
        """
        validator = ContactValidator()
        p = validator.validate_phone(phone.strip(), required=True)
        if validator.errors:
            raise AppValidationErrors(
                validator.errors, origin="ContactService.find_by_phone"
            )

        canonical = ContactValidator.canonicalize_phone(p)
        result = self._repo.find_by_phone(canonical)
        if not result:
            raise AppWarning(
                code="CONTACT_NOT_FOUND",
                origin="ContactService.find_by_phone",
                search_field="phone",
                phone=phone,
            )
        return result

    def update(
        self, contact_id: int, first_name: str, last_name: str, email: str, phone: str
    ) -> Contact:
        """Update an existing contact, validating email/phone not used by others.

        Args:
            contact_id: ID of contact to update.
            first_name: New first name.
            last_name: New last name.
            email: New email address.
            phone: New phone number.

        Returns:
            Updated Contact.

        Raises:
            AppValidationErrors: If validation fails or duplicate is detected.
        """
        # Create contact — entity validates its own data and canonicalises phone
        contact = Contact.create(
            contact_id=contact_id,
            first_name=ContactValidator.normalize_name(first_name),
            last_name=ContactValidator.normalize_name(last_name),
            phone=phone.strip(),
            email=ContactValidator.normalize_string(email),
        )

        # Check business rules
        policy = ContactPolicy()

        # Check if email already exists (for another contact)
        contact_found = self._repo.find_by_email(contact.email)
        policy.ensure_unique_email(contact_found, contact)

        # Check if phone already exists (for another contact)
        if contact.phone:
            contact_found = self._repo.find_by_phone(contact.phone)
            policy.ensure_unique_phone(contact_found, contact)

        if policy.errors:
            raise AppValidationErrors(policy.errors, origin="ContactService.update")

        return self._repo.update(contact)

    def list_all(self) -> Sequence[Contact]:
        """List all contacts.

        Returns:
            List of all contacts.

        Raises:
            AppWarning: If no contacts exist in the system.
        """
        contacts = self._repo.list_all()
        if not contacts:
            raise AppWarning(
                code="EMPTY_CONTACT_LIST",
                origin="ContactService.list_all",
            )
        return contacts

    def delete(self, contact_id: int) -> bool:
        """Delete a contact by ID.

        Args:
            contact_id: ID of contact to delete.

        Returns:
            True if contact was deleted, False if not found.
        """
        return self._repo.delete(contact_id)
