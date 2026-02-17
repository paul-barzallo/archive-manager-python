# AGENTS.md - Context & Guidelines for Archive Manager

## Project Overview

**Archive Manager Python** is a clean architecture-based contact management system. It is designed to be interface-agnostic, currently supporting a CLI adapter and soon to support a REST API adapter.

## Architecture

The project follows **Clean Architecture / Hexagonal Architecture** principles.

### Layers (Inner to Outer)

1. **Core (Domain)** (`src/archive_manager/core`)
   * **Entities**: Pure Python objects representing business concepts (e.g., `Contact`).
   * **Interfaces**: Abstract base classes defining contracts for repositories and services.
   * **Errors**: Domain-specific exceptions (`AppValidationErrors`).
   * **No external dependencies** (except standard library).

2. **Application** (`src/archive_manager/application`)
   * **Services**: Orchestrate business logic (`ContactService`).
   * **DTOs**: Data Transfer Objects for moving data between layers.
   * **Policies**: specific business rules.
   * Depends only on **Core**.

3. **Adapters** (`src/archive_manager/adapters`)
   * **CLI**: Console interface using `rich` and `InquirerPy`.
   * **API**: REST interface using `FastAPI` and `Uvicorn`.
   * **Controllers**: Handle input/output for specific interfaces and call Services.

4. **Infrastructure** (`src/archive_manager/infrastructure`)
   * **Persistence**: Database implementations (SQLAlchemy/SQLite).
   * **Config**: Settings management (Pydantic Settings).
   * **Logging**: structured logging configuration.

## Coding Standards

### Typing

* Use **Type Hints** everywhere.
* Use `typing.Sequence` for lists/arrays unless `list` specific methods are needed.
* Use `typing.Self` for factory methods.
* Avoid `Any` unless absolutely necessary.

### Documentation

* **Google Style Docstrings** are mandatory for all modules, classes, and methods.
* Include `Args`, `Returns`, and `Raises` sections.
* File headers should include `#!/usr/bin/env python3`.

### Error Handling

* Use custom exceptions from `core.errors`.
* **Validation**: `AppValidationErrors` for input/logic issues.
* **Not Found**: Return `None` or raise specific exceptions depending on context (Repo returns `None`, Service might raise).

### Pydantic

* Used for Configuration and DTOs (preferred).
* Settings are loaded from environment variables or `.env` files.

## Development Workflow

* **Testing**: `pytest` for unit and integration tests.
* **Dependency Management**: `pyproject.toml` (standard PEP 621).
* **Linter**: `ruff`.

## Important Files

* `pyproject.toml`: Dependencies and tool config.
* `src/archive_manager/infrastructure/config/settings.py`: Global settings.
* `src/archive_manager/application/services/`: Business Logic location.

---
Created by Copilot Agent - Feb 2026
