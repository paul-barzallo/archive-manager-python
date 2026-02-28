# API Implementation Guidelines

## Overview

The REST API adapter is implemented with **FastAPI** and runs alongside the
CLI adapter, reusing the same Application and Core layers.

## Current Structure

```text
adapters/api/
|-- __init__.py
|-- main.py               # FastAPI app factory and uvicorn runner
|-- deps.py               # Long-lived dependency container
|-- handlers.py           # Exception handlers
|-- routers/
|   |-- __init__.py
|   `-- contacts.py       # Contact endpoints
`-- schemas/
    |-- __init__.py
    |-- base.py           # Shared response models
    `-- contacts.py       # Contact request/response models
```

## Dependency Injection

- `main.py` creates the `FastAPI` app and configures the lifespan hook.
- `ApiContainer` in `deps.py` wires `SqliteConnection`,
  `SqliteContactRepository`, and `ContactService`.
- The container is stored in `app.state.container` and closed on shutdown.
- Route handlers obtain the service through `get_contact_service()`.

## Data Contracts

- **Requests** use dedicated Pydantic models from
  `adapters/api/schemas/contacts.py`.
- **Responses** adapt application DTOs into API response models.
- Shared envelopes such as `HealthResponse` and error payloads live in
  `adapters/api/schemas/base.py`.

## Error Handling

`handlers.py` centralizes exception handling and translates domain errors into
HTTP responses:

1. `AppValidationErrors` -> `400 Bad Request`
2. `AppWarning` -> status from i18n metadata, defaulting to `404 Not Found`
3. `AppError` -> status from i18n metadata, defaulting to `409 Conflict`
4. `AppInfrastructureError` -> status from i18n metadata, defaulting to
   `500 Internal Server Error`

Messages are localized using the `Accept-Language` header.

## Configuration

- API settings live in `src/archive_manager/infrastructure/config/settings.py`
  under `ApiSettings`.
- Defaults are:
  - Host: `127.0.0.1`
  - Port: `8000`
  - Reload: `false`
- Runtime entry point: `archive-manager api`

## Validation

- API-specific tests live in `tests/unit/api/`.
- API checks run in `.github/workflows/api-ci.yaml`.

## Context Links

- [Contact service](../src/archive_manager/application/services/contact_service.py)
- [API app factory](../src/archive_manager/adapters/api/main.py)
- [API handlers](../src/archive_manager/adapters/api/handlers.py)
