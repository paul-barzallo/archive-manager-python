# API Implementation Guidelines

## Overview

We are adding a REST API adapter using **FastAPI** + **Uvicorn**. This adapter will sit alongside the existing CLI adapter, reusing the Application and Core layers.

## Architecture Strategy

### 1. Adapter Location

New directory: `src/archive_manager/adapters/api`

Structure:

```text
adapters/api/
├── __init__.py
├── main.py           # FastAPI App definition
├── deps.py           # Dependency Injection (Database, Services)
├── routers/          # API Endpoints
│   ├── __init__.py
│   └── contacts.py   # Contact endpoints
└── schemas.py        # Pydantic models (if separate from DTOs)
```

### 2. Dependency Injection

* The existing CLI instantiates services manually.
* The API will use FastAPI's `Depends` system.
* `deps.py` will handle opening/closing database sessions and creating Service instances per request.

### 3. Data Transfer

* **Request**: `ContactCreate` (Pydantic model) -> `ContactService`
* **Response**: `ContactDTO` -> `ContactResponse` (Pydantic model)
* **Goal**: Minimize duplication. If possible, adapt `ContactDTO` to be Pydantic-compatible or create lightweight wrappers.

### 4. Error Handling

* Middleware or centralized exception handler in `main.py`.
* Map `AppValidationErrors` -> HTTP 400 Bad Request.
* Map `AppNotFoundError` (if exists) -> HTTP 404 Not Found.
* Internal errors -> HTTP 500.

### 5. Configuration

* Add `APISettings` to `src/archive_manager/infrastructure/config/settings.py`.
* Defaults: Host `127.0.0.1`, Port `8000`.

## Implementation Steps

1. **Settings**: Update `settings.py`.
2. **Dependencies**: Create `adapters/api/deps.py` for DB session handling.
3. **Router**: Create `adapters/api/routers/contacts.py` implementing CRUD using `ContactService`.
4. **App**: Create `adapters/api/main.py` assembling the app.
5. **Entry Point**: Add `archive-api` script to `pyproject.toml`.

## Context Links

* [Service Reference](../src/archive_manager/application/services/contact_service.py) - The business logic we are wrapping.
