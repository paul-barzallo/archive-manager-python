# Domain Map

This document outlines the core domain modules of the `archive-manager-python` project and the interfaces they expose. The architecture is designed as a modular platform where each domain area is implemented as an independent service module.

## Current Modules

### 1. Contacts (`contacts`)

The `contacts` module is currently the most mature domain in the application. It handles the lifecycle, validation, and persistence of contact entities.

#### Exposed Interfaces

* **`ContactService`**: The primary entry point for business logic related to contacts.
  * **Responsibilities**:
    * CRUD operations (Create, Read, Update, Delete).
    * Duplicate detection (e.g., preventing multiple contacts with the same email or phone number).
    * Canonical phone search (finding contacts by their standardized E.164 phone number).
  * **Location**: `src/archive_manager/application/services/contact_service.py` (Implementation) / `src/archive_manager/core/interfaces/service.py` (Contract)

* **`ContactRepository`**: The interface for data persistence operations.
  * **Responsibilities**:
    * Abstracting the underlying database (e.g., SQLite, PostgreSQL).
    * Executing CRUD and search queries specific to contacts.
  * **Location**: `src/archive_manager/core/interfaces/contact_repository.py`

## Future Modules (Planned)

As the platform evolves, additional modules are expected to be added following the same Clean Architecture principles:

* `tasks`
* `events`
* `notes`
* `projects`
