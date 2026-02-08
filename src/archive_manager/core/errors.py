#!/usr/bin/env python3
"""Application-specific exceptions for error handling.

Exception Hierarchy (from least to most severe):
-------------------------------------------------

1. AppWarning: Non-blocking warnings that allow retry.
   - Reintentable: YES - user can acknowledge and retry
   - User sees: Warning message
   - Example: Empty contact list, contact not found in search

2. AppValidationErrors: Aggregates validation errors for batch reporting.
   - Reintentable: YES - user can fix input and retry
   - User sees: All validation errors at once
   - Example: Invalid email format, name too long, required field empty

3. AppError: User-correctable errors, not recoverable in current operation.
   - Reintentable: NO - operation is aborted
   - User sees: Error message with context
   - Example: Trying to update/delete contact that no longer exists,
              duplicate email when creating contact

4. AppInfrastructureError: System errors (5XX equivalent).
   - Reintentable: NO - operation is aborted
   - User sees: Generic "An error occurred" message
   - Logs: Full details for debugging
   - Example: Database connection failed, persistence error

5. Exception (unhandled): Critical unexpected errors.
   - Reintentable: NO - may terminate application
   - User sees: Generic error message
   - Logs: Full stack trace
   - Example: Programming errors, unexpected state

The ``code`` attribute maps to i18n messages in output/error.json or
output/warning.json. The ``origin`` attribute identifies where the exception
was raised for debugging.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class AppException(Exception):
    """Base class for all application-level errors.

    Used as a generic system-level error when more specific types don't apply.

    Attributes:
        code: Message code used by OutputMessages to resolve message/status.
        origin: Source location where the exception was raised (e.g., class.method).
        field: Optional field name associated with the error (for validation errors).
        context: Mapping of placeholder names to values used for formatting.
    """

    def __init__(
        self,
        code: str,
        origin: str,
        field: str | None = None,
        **context: Any,
    ) -> None:
        """Create an application exception with a code and context.

        Args:
            code: Message code present in output/error.json.
            origin: Source location where the exception was raised (REQUIRED).
            field: Optional field name associated with the error.
            **context: Values for formatting the message template.
        """
        super().__init__()
        self.code = code
        self.origin = origin
        self.field = field
        self.context: dict[str, Any] = context or {}

    def __repr__(self) -> str:
        """Return string representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, origin={self.origin!r}, context={self.context!r})"
        )


class AppWarning(AppException):
    """Warning-level issue that allows the user to retry.

    Used for expected "not found" or "empty" conditions in search/list operations.

    Examples:
        - No contacts match the search criteria
        - Contact list is empty
        - Searched contact not found
    """


class AppError(AppException):
    """User-facing business error that aborts the current operation.

    Used when something went wrong that the user should know about,
    but cannot retry in the current context. These are business logic errors.

    Examples:
        - Trying to update a contact that was deleted by another user
        - Trying to restore a contact that doesn't exist
        - Duplicate email/phone detected during create/update
    """


class AppInfrastructureError(AppException):
    """Infrastructure/system errors (5XX equivalent).

    Used for errors related to external systems, databases, file systems,
    network, etc. These are NOT business logic errors but technical failures.

    Shows generic message to user but logs full details for debugging.

    Examples:
        - Database connection failed
        - File system read/write error
        - Network timeout
        - ORM/SQL errors
    """


class AppValidationErrors(Exception):
    """Aggregates multiple validation errors for batch reporting.

    Used when validating user input to collect all errors before showing them.
    The operation can be retried after the user fixes the input.

    Examples:
        - Multiple fields have invalid format
        - Required fields are missing
        - Field values exceed length limits
    """

    def __init__(self, errors: Sequence[AppError], origin: str) -> None:
        """Create a validation errors collection.

        Args:
            errors: Sequence of AppError instances to aggregate.
            origin: Source location where the validation failed.
        """
        super().__init__()
        self.errors = errors
        self.origin = origin

    def __repr__(self) -> str:
        """Return string representation of the validation errors."""
        codes = [err.code for err in self.errors]
        return f"AppValidationErrors(origin={self.origin!r}, codes={codes})"
