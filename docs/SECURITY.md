# Security

This document outlines the security practices and sensitive areas within the `archive-manager-python` project.

## Input Validation

The application strictly validates all input data before creating or updating entities. This is primarily handled by the `ContactValidator` class.

### `ContactValidator`

* **Responsibilities**:
  * Validates all fields (e.g., name, email, phone) against predefined rules (regex, length, format).
  * Ensures that only valid data enters the core domain.
  * Raises `AppValidationErrors` if any validation fails, aggregating all errors for the user.

## Database Integrity

The application relies on the database to enforce data integrity and prevent invalid states.

### SQL Triggers and Constraints

* **NOT NULL Constraints**: Ensure that required fields (e.g., name, email) are always present.
* **Phone Number Validation**: SQL triggers enforce the 7-15 digit range for phone numbers, ensuring consistency even if data is inserted directly into the database.
* **Unique Constraints**: Prevent duplicate entries (e.g., multiple contacts with the same email or phone number).

## Dependency Injection

The project uses Dependency Injection to manage configuration and database connections securely.

### Secure Practices

* **No Global State**: Configuration and database connections are injected (e.g., via `ApiContainer` in `src/archive_manager/adapters/api/deps.py`), avoiding global state and hardcoded secrets.
* **Environment Variables**: Sensitive configuration (e.g., database credentials, API keys) is loaded from environment variables using `pydantic-settings`.
* **Isolation**: Dependencies are isolated per request or operation, preventing cross-contamination of data or state.
