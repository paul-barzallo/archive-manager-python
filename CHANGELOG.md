# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-02-16

### Added

- **API modularization**: FastAPI adapter was split into focused modules
  (`deps`, `handlers`, `routers`, and `schemas`) to reduce coupling and
  improve maintainability.
- **API i18n responses**: Exception handlers now localize domain errors using
  `Accept-Language` and return translated messages (for example, Spanish).
- **API response contracts**: Contact schemas were separated into dedicated
  modules (`schemas/base.py`, `schemas/contacts.py`) and exported via
  `schemas/__init__.py` for consistent imports.

### Changed

- **Paginated contact list**: `list_contacts` now applies a bounded limit
  (default and maximum: 20) with offset-based paging metadata.
- **List navigation**: Contact listing supports page navigation when
  there are more than 10 contacts in total.
- **Table footer metadata**: Contact table footer now shows current page,
  total pages, and displayed range (for example, `Page 2 of 3 - from 21 to 40 of 52`).
- **i18n caching behavior**: `I18nMenus` and `I18nTables` return defensive
  copies of cached typed objects; loader classes keep raw JSON cache access.
- **DTO boundary**: `ContactPageDTO` is now defined in the application DTO
  module and shared by adapters.
- **CLI entrypoint composition root**: CLI wiring now lives in
  `adapters/cli/main.py`.
- **CLI architecture simplification**: Contact CLI states now call
  `ContactService` directly through `AppContext.service` (no adapter
  controller layer in the runtime flow).
- **Integration testing path**: Contact integration tests now exercise a
  service-backed adapter client (`Service -> Repository -> Database`) while
  keeping DTO-level assertions.
- **Documentation alignment**: `README.md`, `DEVELOPMENT.md`,
  `ARCHITECTURE.md`, and `API_GUIDELINES.md` were updated to reflect the
  service-driven CLI design.

### Removed

- **Obsolete CLI controller files**: Removed
  `adapters/cli/base_controller.py` and `adapters/cli/contact_controller.py`.
- **Obsolete controller protocol**: Removed
  `core/interfaces/controller.py` and its export from
  `core/interfaces/__init__.py`.

## [0.1.0] - 2026-02-08

### Initial release

#### Architecture

- **Clean Architecture**: Four-layer structure (`core/`, `application/`,
  `infrastructure/`, `adapters/`) with strict inward dependency rule.
- **Protocol contracts**: `Entity`, `Repository`, `ContactRepository`,
  `Service`, `Controller`, and `DBConnection` defined in `core/interfaces/`.
- **Generic base classes**: `BaseService(ABC, Service, Generic[TRepository])`
  and `BaseCslController(ABC, Controller, Generic[TService])` satisfy their
  protocols and provide type-safe dependency access.
- **BaseContactRepository**: Abstract base with shared duplicate-detection
  logic in `infrastructure/persistence/`, generic over connection type.
- **Entity factory pattern**: `create()` for validated user input and
  `from_persistence()` for trusted storage reconstruction.
- **Dependency injection**: All components were wired in `cli.py` (migrated
  later to `adapters/cli/main.py`) with no global singletons. I18n classes
  configured at startup via `configure()`.
- **State-machine pattern**: CLI navigation via state classes with
  `@handle_errors` decorator for centralised error handling.

#### Features

- **Contact module**: Create, read, update, soft-delete, and search by
  name (partial match), email (exact), and phone (canonical).
- **Phone canonicalisation**: Different formatting of the same number
  detected as duplicate (e.g. `"+34 600 000 000"` and `"+34600000000"`).
- **Duplicate detection**: `ContactPolicy` business rules enforced before
  persistence.
- **SQLAlchemy persistence**: SQLite storage with WAL mode, ORM, session
  management, and automatic database bootstrap.
- **SQL triggers**: NOT NULL enforcement and `updated_at` auto-update.
  Format validation handled by `ContactValidator` in the application layer.
- **Internationalization**: English and Spanish support with JSON-based
  message, menu, and table loaders.
- **Error hierarchy**: `AppWarning`, `AppValidationErrors`, `AppError`,
  `AppInfrastructureError` with error codes, origin, and context.
- **Configuration**: Pydantic-based YAML with environment-specific overrides
  and CLI flags.
- **Logging**: Rotating file handler (10 MB, 5 backups) separated by
  severity level. Log messages always in English.
- **Console UI**: Rich tables and InquirerPy interactive prompts.

#### Development and Testing

- **248 pytest tests** organised by layer (unit and integration).
- **In-memory SQLite** fixtures for fast, isolated test execution.
- **i18n synchronisation tests** for cross-language key consistency.
- **Import structure tests** for dependency rule compliance.
- **CI/CD**: GitHub Actions workflow (Ubuntu, Python 3.11 and 3.12).
- **Pre-commit hooks**: ruff (linter/formatter), mypy (type checker).
- **Task runner**: PowerShell script (`tasks.ps1`) for test, lint, format,
  check, clean, and install.

#### Documentation

- **`ARCHITECTURE.md`**: Layer descriptions, dependency injection, error
  hierarchy, database strategy, trigger philosophy.
- **`DEVELOPMENT.md`**: Developer setup, import rules, naming conventions,
  entity pattern, error conventions, i18n workflow.
- **`README.md`**: Project overview, quick start, configuration, project
  layout.
- **`CHANGELOG.md`**: This file.
- **MIT License**.
