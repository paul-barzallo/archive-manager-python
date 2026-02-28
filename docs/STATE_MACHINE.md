# State Machine

This document describes the implementation of the state machine used in the Command Line Interface (CLI) of the `archive-manager-python` application. The state machine orchestrates user interaction, menu navigation, and business logic execution.

## CLI State Machine Implementation

The CLI state machine is located in `src/archive_manager/adapters/cli/states/`. It follows a pattern where each state represents a specific screen or action in the CLI.

### `BaseState`

* **Description**: An abstract base class that all concrete states must inherit from.
* **Responsibilities**:
  * Provides a common interface for executing state logic (`run()`).
  * Includes a `@handle_errors` decorator to catch and handle application-specific exceptions (`AppException`) gracefully, displaying appropriate messages to the user.

### Concrete States

Concrete states implement the specific logic for each screen or action. Examples include:

* **`MainContactMenuState`**: Displays the main menu for managing contacts (e.g., Add, List, Search, Exit).
* **`_ListContactsState`**: Handles the logic for listing all contacts, interacting with the `ContactService` to retrieve data and the `CslUI` to display it.

### State Transitions

State transitions occur by returning the next state instance from the `run()` method.

* **Next State**: If a state returns another state instance, the CLI loop continues with the new state.
* **Exit**: If a state returns `None`, the CLI loop terminates, and the application exits.

## Orchestration

The state machine orchestrates the interaction between the user, the UI components (`CslUI`), and the business logic (`ContactService`).

* **User Input**: States use `CslUI` to prompt the user for input (e.g., selecting a menu option, entering contact details).
* **Business Logic**: States call methods on the `ContactService` to perform operations (e.g., creating a contact, searching for a contact).
* **Output**: States use `CslUI` to display results, warnings, or errors to the user.
