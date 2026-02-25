# Errors

This document catalogs the domain error hierarchy used in the `archive-manager-python` application. All application-specific exceptions are defined in `src/archive_manager/core/errors.py`.

## Exception Hierarchy

The application uses a structured exception hierarchy, ordered from least to most severe:

### 1. `AppWarning`

* **Description**: Non-blocking warnings that allow the user to retry the operation.
* **Retryable**: YES - user can acknowledge and retry.
* **User Experience**: Sees a warning message.
* **Examples**: Empty contact list, contact not found in search.

### 2. `AppValidationErrors`

* **Description**: Aggregates multiple validation errors for batch reporting.
* **Retryable**: YES - user can fix the input and retry.
* **User Experience**: Sees all validation errors at once (e.g., invalid email format, name too long).
* **Examples**: Invalid email format, name too long, required field empty.

### 3. `AppError`

* **Description**: User-correctable errors, but the current operation is aborted.
* **Retryable**: NO - operation is aborted.
* **User Experience**: Sees an error message with context.
* **Examples**: Trying to update/delete a contact that no longer exists, duplicate email when creating a contact.

### 4. `AppInfrastructureError`

* **Description**: System errors (equivalent to HTTP 5XX).
* **Retryable**: NO - operation is aborted.
* **User Experience**: Sees a generic "An error occurred" message.
* **Logs**: Full details are logged for debugging.
* **Examples**: Database connection failed, persistence error.

### 5. `Exception` (Unhandled)

* **Description**: Critical unexpected errors.
* **Retryable**: NO - may terminate the application.
* **User Experience**: Sees a generic error message.
* **Logs**: Full stack trace is logged.
* **Examples**: Programming errors, unexpected state.

## Error Attributes

All application errors (`AppException` and its subclasses) carry the following attributes:

* **`code`**: A string code that maps to i18n messages in `output/error.json` or `output/warning.json`.
* **`origin`**: Identifies where the exception was raised for debugging purposes.
* **`context`**: Additional context or data related to the error.
