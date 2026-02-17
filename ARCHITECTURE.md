# Architecture

## Overview

Archive Manager is a console application built following Clean Architecture
principles. The codebase is organised into four layers with a strict
dependency rule: outer layers depend on inner layers, never the reverse.

The project is designed as a modular platform where each domain area
(contacts, documents, etc.) is implemented as an independent service module
that plugs into the shared architecture. The first module manages contacts.

## Dependency Rule

```text
Adapters  -->  Infrastructure  -->  Application  -->  Core
(CLI)          (DB, i18n, cfg)      (services)       (entities, interfaces)
```

Inner layers define contracts via Python protocols. Outer layers provide
concrete implementations. No module in `core/` imports from `application/`,
`infrastructure/`, or `adapters/`.

## Layers

### 1. Core (`core/`)

The domain layer. It has no external dependencies.

- **`entities/`** -- Domain models with validation and factory methods.
  - `BaseEntity`: Abstract base class defining `create()` and
    `from_persistence()` factory methods.
  - `Contact`: Contact entity with field validation and phone
    canonicalisation.
  - `validators/ContactValidator`: Field-level validation (regex, length,
    format) and normalisation helpers.
- **`errors.py`** -- Application exception hierarchy (see Error Handling).
- **`interfaces/`** -- Protocol contracts consumed by all layers.
  - `Entity`: Structural contract for domain entities.
  - `Repository`: Marker protocol for all repositories.
  - `ContactRepository`: Protocol defining CRUD and search operations.
  - `Service`: Protocol contract for application services.
  - `DBConnection`: Protocol contract for database connections.

### 2. Application (`application/`)

Use-case and business-rule layer. Depends only on `core/`.

- **`services/`**
  - `BaseService(ABC, Service, Generic[TRepository])`: Abstract base that
    satisfies the `Service` protocol and provides typed repository access.
  - `ContactService`: Business logic for contact CRUD, duplicate detection,
    and canonical phone search.
  - `policies/ContactPolicy`: Uniqueness rules evaluated before persistence.
- **`dto/`**
  - `ContactDTO`: Data-transfer object for adapter-service boundaries.
  - `ContactPageDTO`: Paginated list response DTO (`contacts`, `total`,
    `limit`, `offset`) with derived metadata for consumers.

### 3. Infrastructure (`infrastructure/`)

Implements core interfaces and provides integrations with external systems.
Depends only on `core/`.

- **`config/`** -- Application settings and runtime configuration.
  - `settings.py`: Pydantic-based YAML configuration, dependency-injected.
  - `logging.py`: Centralised logging with `RotatingFileHandler`.
  - `session.py`: Runtime session state (language, debug flag).
  - `constants.py`: Service name registry.
- **`persistence/`** -- Database access.
  - `BaseContactRepository(ContactRepository, ABC, Generic[TConnection])`:
    Abstract base with shared duplicate-detection logic and typed connection.
  - `SqliteContactRepository`: SQLite-specific implementation.
  - `db/SqliteConnection`: SQLAlchemy engine and session management.
  - `db/sqlite_bootstrap.py`: Executes SQL scripts on first run.
  - `db/orm/ContactORM`: SQLAlchemy ORM model.
  - `mappers/ContactMapper`: Bidirectional entity-ORM conversion.
- **`i18n/`** -- Internationalisation.
  - `messages.py`, `menus.py`, `tables.py`: JSON-based i18n with
    thread-safe caching.
  - `loaders.py`: Base loader with file-system access.

### 4. Adapters (`adapters/`)

Delivery mechanisms. Currently provides a CLI adapter.

- **`cli/`**
  - `main.py`: CLI composition root and dependency wiring.
  - `states/BaseState`: State-machine base with `@handle_errors` decorator.
  - `states/contact_states.py`: Concrete states calling `ContactService`
    directly (menus, create, search, edit, delete, list pagination).
  - `ui/CslUI`: Rich-based console UI (menus, tables, prompts).
  - `ui/ContactCslUI`: Contact-specific UI with paginated table footer and
    list navigation actions.

## Entity Factory Pattern

Direct instantiation of entities is blocked (`__init__` raises `TypeError`).
Two factory methods are provided:

| Method | Purpose | Validation |
| ------ | ------- | ---------- |
| `create()` | New entities from user input | Full validation and canonicalisation |
| `from_persistence()` | Reconstruction from trusted storage | No re-validation |

## Phone Canonicalisation

Phone numbers are validated and stored according to ITU-T Recommendation
E.164: 7 to 15 digits with an optional leading `+` for the country code.
The canonical form strips all formatting characters (spaces, dashes,
parentheses) while preserving the international prefix. For example,
`"+34 600 000 000"` becomes `"+34600000000"`. Search queries are also
canonicalised before comparison.

Validation is enforced at three levels:

1. **Application layer**: `ContactValidator` checks digit count (7-15)
   and allowed characters.
2. **SQL triggers**: Defensive checks reject inserts and updates that
   violate the 7-15 digit range.
3. **Schema**: `phone VARCHAR(16)` limits storage to `+` plus 15 digits.

## Dependency Injection

`Settings` is created once in `adapters/cli/main.py` and passed to every
component that requires configuration. There is no global singleton.

```text
adapters/cli/main.py
|-- Settings()
|-- I18nMessages.configure(settings.i18n)
|-- I18nMenus.configure(settings.i18n)
|-- I18nTables.configure(settings.i18n)
|-- SqliteConnection(settings.database)
|   +-- SqliteContactRepository(connection)
|       +-- ContactService(repository)
+-- ContactCslUI()
+-- AppContext(session, ui, service)
+-- run(context)
```

## Data Flow

```text
State Machine --> Service --> Repository --> ORM --> SQLite
      |                                                      ^
      +-- UI (Rich) --> i18n loaders --> JSON resources       |
                                                              |
                     ContactMapper (entity <-> ORM) ----------+
```

## Internationalization

- Resources are shipped inside the package under `resources/i18n/<lang>/`.
- Each language directory contains three subdirectories: `visual/` (prompts,
  labels), `output/` (error, warning, and success messages), and one directory per
  service module (e.g. `contact/` for menus and tables).
- I18n classes (`I18nMessages`, `I18nMenus`, `I18nTables`) are configured
  once at startup via `configure(i18n_settings)` and resolve messages
  through a thread-safe cache.
- Loader classes cache raw JSON mappings; typed menu/table resolvers return
  defensive copies of `I18nMenu` and `I18nTable` so dynamic UI mutations do
  not leak into shared cache state.
- Log messages are always written in English regardless of the user
  interface language.

## Error Handling

The application uses a tiered exception hierarchy:

| Level | Class | Retryable | Example |
| ----- | ----- | --------- | ------- |
| 1 | `AppWarning` | Yes | Empty list, no search results |
| 2 | `AppValidationErrors` | Yes | Invalid email, missing fields |
| 3 | `AppError` | No | Duplicate entry, not found |
| 4 | `AppInfrastructureError` | No | Database failure, I/O error |
| 5 | `AppException` | No | Unexpected application error |
| 6 | `Exception` | No | Unhandled or critical |

All application errors carry:

- `code` -- Error code used for i18n message lookup.
- `origin` -- Source location in `"ClassName.method_name"` format.
- `context` -- Optional keyword parameters for message formatting.

The `@handle_errors` decorator on state classes catches exceptions, logs
them at the appropriate level, and renders localised user messages.

## Database

### Bootstrap

On first run, SQL scripts from `infrastructure/persistence/db/scripts/` are
executed in alphabetical order:

| Script | Purpose |
| ------ | ------- |
| `000_create_table_contacts.sql` | Creates the contacts table with indexes |
| `001_triggers_contacts.sql` | NOT NULL enforcement and `updated_at` auto-update |
| `002_pragma_auto_vacuum.sql` | Incremental auto-vacuum for space reclamation |

### Trigger Philosophy

Triggers are defensive only. They enforce NOT NULL and NOT EMPTY constraints
on required fields and auto-update the `updated_at` timestamp. All format
validation (email regex, phone format, name rules) is handled exclusively
by the application layer via `ContactValidator`.

### Adding New Scripts

1. Create a `.sql` file in `infrastructure/persistence/db/scripts/`.
2. Name it with a numeric prefix for ordering (e.g. `003_new_feature.sql`).
3. Write standard SQL; lines starting with `--` are stripped.

Migrations are not yet supported. Schema changes require deleting the
database file and restarting the application.

## Configuration

Configuration is resolved with the following precedence (highest first):

1. `--debug` CLI flag.
2. Constructor keyword arguments (testing or programmatic use).
3. Environment variables (`APP_` prefix, `__` as nested delimiter).
4. `.env` file (secrets and per-machine overrides).
5. `config.<environment>.yaml` (environment-specific overrides).
6. `config.yaml` (base configuration).
7. Pydantic field defaults.

Static resources are shipped inside the package. Runtime data (database,
logs) is stored under `data/` relative to the project root.

## Logging

Log files are written to `data/logs/` using
`RotatingFileHandler` (10 MB per file, 5 backups):

| File | Level |
| ---- | ----- |
| `debug.log` | DEBUG (only when `--debug` is passed) |
| `info.log` | INFO and above |
| `error.log` | ERROR and above |
