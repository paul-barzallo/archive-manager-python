# Development Guide

This document describes the development environment setup, project
conventions, and workflows for contributing to the project.

## Requirements

- Python 3.11 or newer.
- pip.

## Setup

```bash
git clone https://github.com/Paul-Barzallo/archive-manager-python.git
cd archive-manager-python
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running the Application

```bash
archive-manager
```

Or run the module directly:

```bash
python -m archive_manager.cli
```

## Testing

```bash
python -m pytest
```

Tests are organised by layer under `tests/`:

| Directory | Scope |
| --------- | ----- |
| `unit/entities/` | Domain model validation and canonicalisation |
| `unit/validators/` | Field-level validation rules |
| `unit/services/` | Business logic and policy enforcement |
| `unit/repositories/` | Repository and bootstrap scripts |
| `unit/states/` | State-machine transitions and error handling |
| `unit/views/` | UI rendering and i18n resolution |
| `unit/i18n/` | Message key synchronisation across languages |
| `unit/imports/` | Import structure and dependency rule compliance |
| `unit/cli/` | Entry point and wiring |
| `integration/` | Full-stack CRUD through service, repository, and SQLite |

Integration tests use an in-memory SQLite database for fast, isolated
execution.

Contact module behaviors covered by tests include:

- Create contact.
- Read and display contact detail.
- Update and soft-delete contact.
- Search by name, email, and phone.
- List contacts with bounded pagination (`limit` default/max: 20), including
  page counters and visible range metadata.

## Linting and Formatting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Continuous Integration

The CI pipeline (`.github/workflows/ci.yaml`) runs on every push and
pull request to `main` or `develop`:

1. **Lint**: Ruff format and lint checks (must pass first).
2. **Type check**: mypy static analysis.
3. **Test**: Full test suite on Python 3.11 and 3.12.
4. **Coverage**: Report uploaded as artifact on 3.11.

All checks must pass before a pull request can be merged.

## Branch Strategy

| Branch | Purpose |
| ------ | ------- |
| `main` | Stable releases |
| `develop` | Integration branch for the next release |
| `feature/*` | Individual features or changes |

Workflow: `feature/*` -> `develop` (via PR with CI) -> `main` (release).

## Task Runner (Windows)

```powershell
.\tasks.ps1 test
.\tasks.ps1 lint
.\tasks.ps1 format
.\tasks.ps1 check
.\tasks.ps1 clean
.\tasks.ps1 install
```

## Import Rules

The project enforces strict dependency boundaries between layers:

| From | May import |
| ---- | ---------- |
| `core/` | Nothing else in the project |
| `application/` | `core/` only |
| `infrastructure/` | `core/` only |
| `adapters/` | `core/`, `application/`, `infrastructure/` |
| `cli.py` | All layers (wiring root) |

Within a package, two conventions apply:

- **Cross-package imports** use `__init__.py` shortcuts
  (e.g. `from archive_manager.core.interfaces import Service`).
- **Intra-package (sibling) imports** use direct file paths
  (e.g. `from archive_manager.core.interfaces.service import Service`)
  to avoid circular imports caused by `__init__.py` initialisation order.

## Adding New Components

1. Define the interface (protocol) in `core/interfaces/`.
2. Implement it in `infrastructure/` or `adapters/`.
3. Wire it in `cli.py`.

Abstract base classes that depend on external libraries (e.g. SQLAlchemy)
belong in `infrastructure/`, not in `core/interfaces/`.

## Naming Conventions

- **Protocols**: Named after the concept (`Service`, `Controller`,
  `Repository`, `Entity`, `DBConnection`).
- **Abstract base classes**: Prefixed with `Base` (`BaseService`,
  `BaseCslController`, `BaseEntity`, `BaseContactRepository`, `BaseState`).
- **Concrete classes**: Named after the implementation
  (`ContactService`, `ContactCslController`, `SqliteContactRepository`).
- **Filenames**: Follow the class name in snake_case (`base_service.py`,
  `contact_service.py`).
- **Singular form**: All names use singular form (`Contact`, not `Contacts`).

## Dependency Injection

`Settings` is created once in `cli.py` and injected into every component.
There is no global singleton. I18n classes are configured once at startup
via class-level `configure(i18n_settings)` calls.

## Error Conventions

The application uses a tiered exception hierarchy. When raising errors,
follow these guidelines:

| Class | Use case | Retryable |
| ----- | -------- | --------- |
| `AppWarning` | Non-blocking warnings (empty list, no results) | Yes |
| `AppValidationErrors` | Aggregated field validation errors | Yes |
| `AppError` | Domain errors that abort the operation | No |
| `AppInfrastructureError` | System-level failures (database, I/O) | No |

All errors must include:

- `origin` in `"ClassName.method_name"` format.
- `code` matching an i18n message key.
- Validation errors should be collected and raised together via
  `AppValidationErrors`.
- Log messages are always written in English.

## Entity Pattern

Domain entities extend the `BaseEntity` abstract base class. Direct
instantiation via `__init__` is blocked; two factory methods are provided:

| Method | Purpose | Validation |
| ------ | ------- | ---------- |
| `create(**kwargs)` | New entities from user input | Full validation and canonicalisation |
| `from_persistence(**kwargs)` | Reconstruction from trusted storage | No re-validation |

Choose the appropriate factory based on the data source:

| Source | Method |
| ------ | ------ |
| User input (CLI, form) | `create()` |
| Database or cache | `from_persistence()` |
| Tests with valid data | `create()` |
| Tests bypassing validation | `from_persistence()` |

## Phone Canonicalisation

Phone numbers are validated and stored per ITU-T E.164 (7 to 15 digits,
optional leading `+`). Formatting characters are stripped to canonical
form:

| Input | Canonical | Digits |
| ----- | --------- | ------ |
| `+34 600 000 000` | `+34600000000` | 11 |
| `(555) 123-4567` | `5551234567` | 10 |
| `123-456-7890` | `1234567890` | 10 |

Canonicalisation is applied in `Contact.create()` after validation. Search
queries are also canonicalised before comparison.

## Internationalization

All user-facing text lives under `resources/i18n/<lang>/`. When adding or
modifying a message key:

1. Update the key in every language directory (`en/`, `es/`).
2. Run `python -m pytest tests/unit/i18n/test_i18n_sync.py` to verify
   consistency.

Caching and mutation rules:

- `I18nMessageLoader`, `I18nMenusLoader`, and `I18nTablesLoader` cache raw
  JSON dictionaries by file path.
- `I18nMenus` and `I18nTables` return defensive deep copies of typed objects
  (`I18nMenu` / `I18nTable`), so UI layers can safely mutate options/headers
  without contaminating shared cache state.

## Local Data

Local development artifacts (database, logs) live under `data/` and are
ignored by git.
