# Conventions

This document outlines the coding conventions, naming patterns, and architectural patterns used in the `archive-manager-python` project.

## Architectural Patterns

### Clean Architecture

The project strictly follows Clean Architecture principles, organizing code into concentric layers:

1. **Core**: Contains domain entities and interfaces (contracts).
2. **Application**: Contains use cases and domain services.
3. **Infrastructure**: Contains concrete implementations of interfaces (e.g., database repositories, external APIs).
4. **Adapters**: Contains entry points to the application (e.g., CLI, REST API).

Inner layers define contracts via Python protocols, and outer layers provide concrete implementations. Dependencies always point inwards.

### Entity Factory Pattern

Direct instantiation of entities is blocked (`__init__` raises `TypeError`). Entities must be created using specific factory methods:

* `create()`: Used for new input from users or external systems. Performs full validation.
* `from_persistence()`: Used for reconstructing entities from trusted storage (e.g., database). Bypasses validation for performance and reliability.

### Dependency Injection

The project uses Dependency Injection to manage dependencies and avoid global state.

* `Settings` is created once at startup and passed down through the layers.
* There are no global singletons.
* Dependencies are injected via constructors or specific injection mechanisms (e.g., `ApiContainer` in FastAPI).

## Domain Rules

### Phone Canonicalisation

Phone numbers are canonicalised following the ITU-T Recommendation E.164 format:

* Must be between 7 and 15 digits.
* May optionally start with a leading `+`.
* All non-digit characters (except the leading `+`) are stripped during canonicalisation.

## Internationalization (i18n)

* Resources are located in `src/archive_manager/resources/i18n/<lang>/`.
* Log messages are always written in English to ensure consistency for developers and operators.
* User-facing messages (e.g., CLI output, API responses) are translated using the i18n system.
