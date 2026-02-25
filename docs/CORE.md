# Core Domain

This document outlines the data models and core interfaces that form the foundation of the `archive-manager-python` application. These components reside in the `src/archive_manager/core/` directory and define the business rules and contracts for the entire system.

## Data Models (Entities)

The data models represent the core business objects of the application. They are located in `src/archive_manager/core/entities/`.

### `BaseEntity`

* **Description**: An abstract base class that all domain entities must inherit from.
* **Responsibilities**:
  * Provides common attributes like `id`, `created_at`, and `updated_at`.
  * Enforces the Entity Factory Pattern (direct instantiation via `__init__` is blocked).

### `Contact`

* **Description**: The primary domain entity representing a contact.
* **Responsibilities**:
  * Holds contact information (name, email, phone, etc.).
  * Performs field validation upon creation.
  * Handles phone number canonicalisation (converting to ITU-T E.164 format).
  * Provides factory methods: `create()` (for new input with validation) and `from_persistence()` (for reconstructing from trusted storage without validation).

## Core Interfaces (Contracts)

The core interfaces define the contracts that outer layers (Application, Infrastructure, Adapters) must implement. They are located in `src/archive_manager/core/interfaces/`.

### `Entity`

* **Description**: A protocol defining the basic structure of an entity.
* **Responsibilities**: Ensures all entities have an `id` and basic lifecycle methods.

### `Repository`

* **Description**: A generic protocol for data access operations.
* **Responsibilities**: Defines standard CRUD methods (`add`, `get`, `update`, `delete`, `list`) that any repository implementation must provide.

### `ContactRepository`

* **Description**: A specific repository interface for the `Contact` entity.
* **Responsibilities**: Extends the generic `Repository` with contact-specific queries, such as finding by email or canonical phone number.

### `Service`

* **Description**: A protocol defining the structure of a domain service.
* **Responsibilities**: Encapsulates business logic and orchestrates operations between entities and repositories.

### `DBConnection`

* **Description**: An interface representing a database connection.
* **Responsibilities**: Abstracts the underlying database connection mechanism, allowing for dependency injection and easier testing.
