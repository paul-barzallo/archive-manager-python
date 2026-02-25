# AGENTS.md — Rules Folder Operating Guide

This file defines how agents must consume rules from this folder.

## Rule Loading Contract

1. Always load `always.md` first.
2. Then load the role file(s) that match the requested task:
   - `backend.md`
   - `frontend.md`
   - `database.md`
   - `cicd.md`
3. If a task spans multiple roles, apply all relevant role files.

## Conflict Policy

- `always.md` is mandatory baseline and cannot be ignored.
- Role files can add stricter constraints but cannot weaken baseline rules.
- If conflict persists, follow root `AGENTS.md` priority order.

## Notes

- `README.md` in this folder is for humans.
- Agent execution behavior must be defined in `AGENTS.md` files.
