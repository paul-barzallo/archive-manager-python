# Archive Manager

<p align="left">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.11+">
  </a>
  <a href=".github/workflows/ci.yaml">
    <img src="https://img.shields.io/badge/ci-github%20actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="CI">
  </a>
  <a href="docs/ARCHITECTURE.md">
    <img src="https://img.shields.io/badge/architecture-clean-0A7E8C?style=flat" alt="Clean Architecture">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-1F6FEB?style=flat" alt="MIT License">
  </a>
</p>

Archive Manager is a Python CLI for managing archives through independent,
extensible modules. The first implemented module focuses on contact management,
with a structure designed to grow into additional domains over time.

## 🤖 AI Agents Ecosystem

This repository is pioneering an **AI-First Development** approach. We have structured a dedicated ecosystem to help AI agents (like GitHub Copilot or custom subagents) understand, navigate, and contribute to the project autonomously and safely.

> **💡 The Core Principle:** Agents read their instructions from [`AGENTS.md`](AGENTS.md) first, which acts as the central operating manual, routing them to specific rules, workflows, and skills.

### 📂 The `.agents/` Directory

This folder contains the "brain" and behavioral constraints for our AI assistants:

* 🚨 **Rules (`.agents/reglas/`)**: Strict constraints and guidelines.
  * *Example:* [`always.md`](.agents/reglas/always.md) contains mandatory baseline rules (e.g., "Never run `git push`", "Always run `mypy`").
* 🔄 **Workflows (`.agents/workflows/`)**: Step-by-step standard operating procedures for complex tasks.
  * *Example:* [`feature_delivery_workflow.md`](.agents/workflows/feature_delivery_workflow.md) guides an agent from planning to testing and documentation.
* 🧠 **Skills (`.agents/skills/`)**: Domain-specific knowledge bases that agents can read to learn how to perform specific technical tasks.
  * *Example:* [`cloud-functions/SKILL.md`](.agents/skills/cloud-functions/SKILL.md) teaches the agent how to handle specific integrations.

### 📚 The `docs/` Directory (Agent Context)

To maintain a shared understanding of the project's architecture, the `docs/` folder contains context files **written by agents, for agents** (and humans!). This prevents AI hallucinations and ensures consistency across sessions:

* 🗺️ [`DOMAIN_MAP.md`](docs/DOMAIN_MAP.md): What modules exist and what they expose.
* 🌐 [`CORE.md`](docs/CORE.md): Data models and core interfaces.
* 📏 [`CONVENTIONS.md`](docs/CONVENTIONS.md): Naming, language, and architectural patterns.
* ⚠️ [`ERRORS.md`](docs/ERRORS.md): Catalog of domain errors.
* 🛡️ [`SECURITY.md`](docs/SECURITY.md): What to protect and what not to touch.
* 🔄 [`STATE.md`](docs/STATE.md): Domain states of entities.
* 📦 [`DEPENDENCIES.md`](docs/DEPENDENCIES.md): External libraries, why they were chosen, and where they live.
* 🧪 [`TEST_MAP.md`](docs/TEST_MAP.md): What is covered, test types, and fixtures.
* 🏗️ [`ARCHITECTURE.md`](docs/ARCHITECTURE.md): Layer design, DI strategy, and persistence decisions.
* 🛠️ [`DEVELOPMENT.md`](docs/DEVELOPMENT.md): Setup, conventions, i18n workflow, and patterns.

---

## What You Get

| Area | Highlights |
| ---- | ---------- |
| Contact workflows | Create, read, update, soft-delete, and search by name, email, or phone |
| Listing and pagination | Contact list uses a bounded limit (default and max: 20), footer metadata (`page/pages` and `from-to/total`), and next/previous navigation when total results are greater than 10 |
| Duplicate prevention | Phone canonicalization detects equivalent formats (for example, `+34 600 000 000` and `+34600000000`) |
| Internationalization | English and Spanish resources for prompts, menus, and outputs |
| Architecture | Clean Architecture, protocol-based interfaces, and dependency injection |
| Persistence | SQLAlchemy repositories over SQLite with automatic bootstrap |
| CLI experience | Rich terminal UI with InquirerPy interactive prompts |
| Observability | Rotating logs by severity (10 MB, 5 backups) |

## Requirements

* Python 3.11 or newer

## Quick Start

```bash
git clone https://github.com/Paul-Barzallo/archive-manager-python.git
cd archive-manager-python
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -e .
archive-manager cli
```

Run API server:

```bash
archive-manager api
```

Show available commands:

```bash
archive-manager
```

API options:

```bash
archive-manager api --host 0.0.0.0 --port 3000 --reload
```

Open interactive API docs at `http://127.0.0.1:8000/docs`.

## Configuration

Configuration precedence (highest to lowest):

1. `--debug` CLI flag
2. Constructor keyword arguments (tests/programmatic use)
3. Environment variables (`APP_` prefix, `__` nested delimiter)
4. `.env` file
5. `config.{environment}.yaml`
6. `config.yaml`
7. Pydantic defaults

Static resources (i18n JSON files, SQL bootstrap scripts) are bundled in the
package. Runtime artifacts (database and logs) are written under `data/`.

### Secrets

Use `.env` for sensitive values (API keys, tokens, credentials). The file is
excluded from version control; use `.env.example` as a template.

```env
APP_DATABASE__URL=sqlite:///data/db/archive-manager.sqlite
APP_DEBUG=true
```

## Storage and Logging

SQLite database:

* Created automatically on first run
* Stored in `data/db/`

Rotating logs (`RotatingFileHandler`) in `data/logs/`:

| File | Level |
| ---- | ----- |
| `debug.log` | DEBUG (only with `--debug`) |
| `info.log` | INFO and above |
| `error.log` | ERROR and above |

All log messages are emitted in English, regardless of UI language.

## Internationalization

Language resources live under `resources/i18n/{lang}/`:

| Directory | Purpose |
| --------- | ------- |
| `visual/` | Prompts, labels, confirmations, field names |
| `output/` | Error, warning, and success messages |
| `contact/` | Contact-module menus and table layouts |

Language defaults to the system locale and can be overridden in `config.yaml`.

## Development

Run tests:

```bash
python -m pytest
```

Lint and format:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

Windows task runner:

```powershell
.\tasks.ps1 test
.\tasks.ps1 lint
.\tasks.ps1 format
.\tasks.ps1 check
.\tasks.ps1 clean
.\tasks.ps1 install
```

## Continuous Integration

Pushes and pull requests to `main` or `develop` run
`.github/workflows/ci.yaml` with:

1. Lint (Ruff format + lint checks)
2. Type check (mypy)
3. Tests (Ubuntu and Windows, Python 3.11 and 3.12)
4. Coverage artifact upload

The test stage depends on lint and type-checking. All checks must pass before
merge.

## Project Layout

```text
src/archive_manager/
├── __init__.py             # Entry point dispatcher (cli/api)
├── core/                   # Domain layer (no external dependencies)
│   ├── errors.py           #   Exception hierarchy
│   ├── entities/           #   Domain models and validators
│   └── interfaces/         #   Protocol contracts
├── application/            # Use-case layer (depends on core)
│   ├── dto/                #   Data transfer objects
│   └── services/           #   Business logic and policies
├── infrastructure/         # External integrations (depends on core)
│   ├── config/             #   Settings, logging, session
│   ├── i18n/               #   Message, menu, and table loaders
│   └── persistence/        #   Repository, ORM, mappers, bootstrap
├── adapters/               # Delivery mechanisms (depends on all layers)
│   ├── cli/                #   Service-driven state machine and Rich UI
│   │   └── main.py         #   CLI composition root
│   └── api/                #   FastAPI app, dependencies, routers, schemas
└── resources/
    └── i18n/               #   JSON resource files (en/, es/)
```

## Documentation

* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): layer design, DI strategy, errors, persistence decisions
* [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): setup, conventions, i18n workflow, patterns
* [docs/API_GUIDELINES.md](docs/API_GUIDELINES.md): rules and conventions for the REST API
* [docs/DOMAIN_MAP.md](docs/DOMAIN_MAP.md): modules and exposed interfaces
* [docs/CORE.md](docs/CORE.md): data models and core interfaces
* [docs/CONVENTIONS.md](docs/CONVENTIONS.md): naming, language, and architectural patterns
* [docs/ERRORS.md](docs/ERRORS.md): catalog of domain errors
* [docs/SECURITY.md](docs/SECURITY.md): security practices and sensitive areas
* [docs/STATE.md](docs/STATE.md): domain states of entities
* [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md): external libraries and their usage
* [docs/TEST_MAP.md](docs/TEST_MAP.md): testing strategy and coverage areas
* [docs/STATE_MACHINE.md](docs/STATE_MACHINE.md): CLI state machine implementation
* [CHANGELOG.md](CHANGELOG.md): release history

## License

MIT License. See [LICENSE](LICENSE).
