# Domain States

This document details the domain states and the strict lifecycle of entities within the `archive-manager-python` application.

## Entity Lifecycle

The `Contact` entity does not have explicit state machine states (like active/inactive) but has a strict lifecycle managed by factory methods. Direct instantiation of entities is blocked (`__init__` raises `TypeError`).

### `create()`

* **Description**: Used for creating a new entity from user input or external systems.
* **Validation**: Performs full validation of all fields (e.g., name, email, phone) against predefined rules.
* **Usage**: When a user submits a new contact via the CLI or API, the `create()` method is called to instantiate the entity.

### `from_persistence()`

* **Description**: Used for reconstructing an entity from trusted storage (e.g., database).
* **Validation**: Bypasses validation for performance and reliability, assuming the data in the database is already valid.
* **Usage**: When retrieving a contact from the database, the `from_persistence()` method is called to reconstruct the entity without re-validating the data.

## State Transitions

The state transitions of an entity are implicit and occur through the factory methods:

1. **New**: An entity is created using `create()`.
2. **Persisted**: The entity is saved to the database.
3. **Reconstructed**: The entity is retrieved from the database using `from_persistence()`.
4. **Updated**: The entity is modified and saved back to the database.
5. **Deleted**: The entity is soft-deleted (`deleted_at` is set) and excluded
   from active queries.

## State Management

The application relies on the database to manage the state of entities. The
`ContactRepository` interface defines the methods for interacting with the
database, such as `add`, `get`, `update`, `delete`, and `list_all`.
