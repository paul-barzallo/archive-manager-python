# Test Map

This document outlines the testing strategy, fixtures, and coverage areas for the `archive-manager-python` project.

## Testing Strategy

The project uses `pytest` as its primary testing framework. The testing strategy is divided into two main categories: unit tests and integration tests.

### Unit Tests

* **Location**: `tests/unit/`
* **Purpose**: To test individual components (e.g., entities, services, repositories, validators) in isolation.
* **Coverage**: High coverage is expected for core domain logic, validation rules, and service methods.
* **Mocking**: External dependencies (e.g., database, API) are mocked or stubbed to ensure tests run quickly and reliably.

### Integration Tests

* **Location**: `tests/integration/`
* **Purpose**: To test the interaction between multiple components (e.g., service and repository, API and database).
* **Coverage**: Focuses on critical user flows and end-to-end scenarios.
* **Database**: Uses an in-memory SQLite database (`sqlite:///:memory:`) for complete isolation and fast execution.

## Fixtures

Fixtures are defined in `tests/conftest.py` and provide reusable setup and teardown logic for tests.

### Key Fixtures

* **`_configure_i18n`**: Configures the internationalization system for testing, ensuring consistent language settings.
* **`test_settings`**: Provides a mock configuration object for testing, overriding production settings.
* **`sqlite_connection`**: Creates an in-memory SQLite database connection for testing, ensuring isolation between tests.
* **`sql_repository`**: Provides a concrete implementation of the `ContactRepository` using the in-memory SQLite database.
* **`service`**: Provides an instance of the `ContactService` configured with the `sql_repository` and `test_settings`.

## Coverage Areas

The test suite covers various areas of the application, ensuring comprehensive testing of all components.

### `tests/unit/`

* **`api/`**: Tests for FastAPI endpoints, request validation, and response formatting.
* **`cli/`**: Tests for CLI commands, argument parsing, and user interaction.
* **`entities/`**: Tests for domain entities, field validation, and factory methods.
* **`i18n/`**: Tests for internationalization resources, translation functions, and language fallback.
* **`imports/`**: Tests for package import integrity, dependency availability,
  and circular-import regressions.
* **`repositories/`**: Tests for database repositories, CRUD operations, and custom queries.
* **`services/`**: Tests for domain services, business logic, and orchestration.
* **`states/`**: Tests for CLI state machine states, transitions, and error handling.
* **`validators/`**: Tests for input validation rules, regex patterns, and error aggregation.
* **`views/`**: Tests for UI components, formatting, and display logic.

### `tests/integration/`

* **`test_contact_flow.py`**: Tests the complete lifecycle of a contact, from creation to deletion, verifying the interaction between the service, repository, and database.
