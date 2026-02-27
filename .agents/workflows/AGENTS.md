# AGENTS.md — Workflows Folder Operating Guide

This file provides agent behavior for workflow documents.

## Usage Contract

- Select exactly one primary workflow per task.
- Execute workflow steps in order unless the user explicitly requests a deviation.
- If a workflow step conflicts with `.agents/reglas/always.md`, the rules win.

## Notes

- `README.md` in this folder is for humans.
- Workflow files define execution flow, not rule priority.
