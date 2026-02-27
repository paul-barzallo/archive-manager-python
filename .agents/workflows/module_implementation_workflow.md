# Module Implementation Workflow

Use this workflow to implement a completely new module from scratch (e.g., `tasks`, `notes`, `events`).
**Prerequisite**: The user must have agreed on the module name, scope, and entities (e.g., via the *Module Ideation Workflow*).

## 1. Scaffolding & Core Domain

- [ ] **Create Entity**:
  - Create `src/archive_manager/core/entities/<module_name>.py`.
  - Define the data class (using `dataclass` or Pydantic if used).
  - Implement validation logic (e.g., `validate()`).
- [ ] **Create Repository Interface**:
  - Create abstract base class in `src/archive_manager/core/interfaces/repository.py` (or a new file if needed).
  - Define methods: `save()`, `get_by_id()`, `list()`, `delete()`.
- [ ] **Create Service**:
  - Create `src/archive_manager/application/services/<module_name>_service.py`.
  - Implement business logic.
  - Inject the repository interface.

## 2. Infrastructure & Persistence

- [ ] **Implement Repository**:
  - Create `src/archive_manager/infrastructure/persistence/<module_name>_repository.py`.
  - Implement the interface using the chosen storage mechanism (e.g., SQLAlchemy/SQLite).
- [ ] **Update Database Schema**:
  - If using SQL, add the table definition.
  - Ensure migrations or bootstrap logic runs (e.g., `infrastructure.persistence.repositories.sql_repository.py` or similar mapping).

## 3. Application Layer (DTOs & Validation)

- [ ] **Create DTOs**:
  - Create `src/archive_manager/application/dto/<module_name>_dto.py` if strict DTOs are used.
- [ ] **Validation**:
  - Ensure input data is validated before touching the domain entities.

## 4. Delivery Mechanism (CLI & API)

- [ ] **CLI Implementation**:
  - Create specific command file `src/archive_manager/adapters/cli/<module_name>_commands.py` (or similar).
  - Add commands: `add`, `list`, `show`, `edit`, `delete`.
  - Register the new command group in `src/archive_manager/adapters/cli/main.py`.
- [ ] **API Implementation**:
  - Create router `src/archive_manager/adapters/api/routers/<module_name>.py`.
  - Define endpoints (GET/POST/PUT/DELETE).
  - Register router in `src/archive_manager/adapters/api/main.py`.

## 5. Testing

- [ ] **Unit Tests**:
  - Test Entities: `tests/unit/entities/test_<module_name>.py`.
  - Test Services: `tests/unit/services/test_<module_name>_service.py`.
- [ ] **Integration Tests**:
  - Test the full flow: `tests/integration/test_<module_name>_flow.py`.

## 6. Verification & Finalization

- [ ] **Type Checking**:
  - Run `mypy .` (or equivalent) to ensure no typing errors.
- [ ] **Run Tests**:
  - Run `pytest` to confirm all tests pass.
- [ ] **Documentation**:
  - Update `docs/DOMAIN_MAP.md` to include the new module.
  - Update `README.md` if it's a major feature.
- [ ] **Commit**:
  - Once valid, commit the changes: `git add .` and `git commit -m "feat: implement <module_name> module"`.
