# AGENTS.md — Central Operating Manual for AI Agents

This is the mandatory entry point for any agent working in this repository.

## Mission

Build and evolve `archive-manager-python` as a modular "super organizer" platform, first improving development automation with AI, then embedding AI capabilities into the product.

## Rule Priority

Follow rules in this exact order:

1. User explicit request.
2. This file (`AGENTS.md`).
3. `agents/reglas/AGENTS.md` + `agents/reglas/always.md` + relevant role file(s).
4. `agents/workflows/AGENTS.md` + selected workflow file.
5. `agents/skills/AGENTS.md` + relevant skill file(s).
6. Core project docs (`README.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/API_GUIDELINES.md`, `docs/DOMAIN_MAP.md`, `docs/CORE.md`, `docs/CONVENTIONS.md`, `docs/ERRORS.md`, `docs/SECURITY.md`, `docs/STATE.md`, `docs/DEPENDENCIES.md`, `docs/TEST_MAP.md`, `docs/STATE_MACHINE.md`, `CHANGELOG.md`).

## Mandatory Rules (Non-negotiable)

1. **Do not write code unless the user explicitly asks for code changes.**
2. Never run `git push` unless explicitly requested by the user.
3. You must **always** consult and strictly follow the rules defined in `agents/reglas/always.md`. This is mandatory for every task.
4. Consult `agents/reglas/AGENTS.md` to find specific rules based on your current role or task.

## Agent Behavior Contract

### Decision Policy

- If request is ambiguous, ask concise clarifying questions before implementation.
- If request is informational, provide analysis without code edits.
- If request explicitly asks implementation, execute end-to-end with validation.

### Scope Control

- Default to MVP scope.
- Do not add "nice to have" extras unless explicitly requested.
- Do not refactor unrelated areas.

### Communication

- Keep progress updates short and action-oriented.
- State assumptions explicitly.
- Report what was changed, where, and how it was validated.

## Tooling Protocol

### File and Code Operations

- Use repository tools to inspect files before editing.
- Use patch-based edits for existing files.
- Prefer targeted reads over broad scans once location is known.

### Verification

- Run the narrowest relevant tests first.
- Expand to broader tests only when needed.
- Report blockers with concrete evidence.

### Safety

- Do not perform destructive operations unless explicitly requested.
- Do not expose secrets from env/config files.

## Project Context (Quick)

- Architecture style: Clean/Hexagonal.
- Current mature domain: contacts.
- Delivery adapters: CLI and API.
- Expected evolution: module-by-module growth (`tasks`, `events`, `notes`, `projects`, ...), then AI features.

## Agent Docs Map

- Rules (agents): `agents/reglas/AGENTS.md`
- Workflows (agents): `agents/workflows/AGENTS.md`
- Skills (agents): `agents/skills/AGENTS.md`
- Rules (human docs): `agents/reglas/README.md`
- Workflows (human docs): `agents/workflows/README.md`
- Skills (human docs): `agents/skills/README.md`

If any file above is missing, create it before relying on it.

## Startup Checklist (for a New Agent with Zero Context)

- [ ] Read this file completely.
- [ ] Read `agents/reglas/AGENTS.md`, then `agents/reglas/always.md`, then relevant role rule files.
- [ ] Read `agents/workflows/AGENTS.md` and select one workflow.
- [ ] Read `agents/skills/AGENTS.md` and relevant skills if needed.
- [ ] Confirm current project state from `README.md` and the `docs/` directory (e.g., `docs/ARCHITECTURE.md`, `docs/DOMAIN_MAP.md`).
- [ ] Execute only the scope requested by the user.

## Completion Checklist (before handoff)

- [ ] Request fully addressed.
- [ ] Scope respected (no extra features).
- [ ] Relevant validations executed and reported.
- [ ] Documentation updated when behavior/process changed.

---
Last updated: 2026-02-24
