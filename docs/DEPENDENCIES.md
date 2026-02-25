# Dependencies

This document lists the external libraries used in the `archive-manager-python` project, explains why they were chosen, and specifies which architectural layer they belong to.

## Production Dependencies

These libraries are required for the application to run in production.

### UI/CLI Layer (Adapters)

* **`rich`**: Used for rich text and beautiful formatting in the terminal. Chosen for its ease of use and extensive features for CLI applications.
* **`InquirerPy`**: Used for interactive command-line prompts and menus. Chosen for its user-friendly interface and support for complex input types.
* **`decorator`**: Used for creating decorators that simplify code and improve readability.

### API Layer (Adapters)

* **`fastapi`**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. Chosen for its speed, automatic interactive API documentation, and ease of use.
* **`uvicorn`**: A lightning-fast ASGI server implementation, using `uvloop` and `httptools`. Chosen as the recommended server for FastAPI applications.

### Database Layer (Infrastructure)

* **`SQLAlchemy`**: The Python SQL Toolkit and Object Relational Mapper. Chosen for its flexibility, performance, and support for multiple database backends (e.g., SQLite, PostgreSQL).

### Configuration Layer (Infrastructure)

* **`pydantic`**: Data validation and settings management using Python type annotations. Chosen for its robust validation capabilities and seamless integration with FastAPI.
* **`pydantic-settings`**: Settings management using Pydantic. Chosen for its ability to load configuration from environment variables and `.env` files.
* **`PyYAML`**: A YAML parser and emitter for Python. Chosen for parsing configuration files (e.g., `config.yaml`).

## Development Dependencies

These libraries are used for testing, linting, and formatting during development.

### Testing

* **`pytest`**: A mature full-featured Python testing tool that helps you write better programs. Chosen for its simplicity, powerful fixtures, and extensive plugin ecosystem.
* **`pytest-cov`**: A plugin for `pytest` that produces coverage reports. Chosen for measuring test coverage and ensuring code quality.
* **`httpx`**: A fully featured HTTP client for Python 3, which provides sync and async APIs. Chosen for testing FastAPI endpoints.

### Linting and Formatting

* **`ruff`**: An extremely fast Python linter, written in Rust. Chosen for its speed and comprehensive set of rules.
* **`mypy`**: An optional static type checker for Python. Chosen for catching type-related errors early in the development process.
* **`pre-commit`**: A framework for managing and maintaining multi-language pre-commit hooks. Chosen for enforcing code quality standards before commits are made.
