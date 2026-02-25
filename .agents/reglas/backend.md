# Backend Rules

Apply these rules for backend/domain/application/infrastructure tasks.

- Keep business rules in `application` and `core`, not in adapters.
- Maintain strict typing and repository/service contracts.
- Prefer explicit error handling with existing error hierarchy.
- Add unit tests for new business logic and integration tests when flow-level behavior changes.
