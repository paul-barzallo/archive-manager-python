# Always Rules (Mandatory Baseline)

These rules are always active for every agent and every task.

1. Do not write code unless the user explicitly asks for code changes.
2. Do not run `git push` under any circumstance unless explicitly requested by the user.
3. Keep changes minimal, focused, and reversible.
4. Preserve Clean Architecture boundaries.
5. Never invent files, APIs, commands, outputs, or validation results.
6. Comment all newly added code.
7. When a new feature or a behavior modification is implemented, update `CHANGELOG.md`.
8. When behavior or process changes, update the relevant documentation.
9. When implementing new functionality, add new tests for it.
10. Validate affected behavior before handoff.
11. Always run `npx markdownlint-cli <file> --disable MD013` when modifying or creating Markdown files.
12. Always run `ruff check <file> --fix` and `ruff format <file>` when modifying or creating Python code.
13. Always run `mypy <file>` when modifying or creating Python code to enforce static typing.

If a user request conflicts with these rules, apply root `AGENTS.md` priority policy.
