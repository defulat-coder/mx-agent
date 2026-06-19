# Monorepo Migration Design

## Goal

Restructure the repository into a clear monorepo with separate `backend/` and `frontend/` directories while preserving the current Python backend behavior.

The frontend scope is intentionally minimal: create an empty placeholder `frontend/` with documentation only. No JavaScript framework, package manager, build step, or UI implementation will be introduced in this migration.

## Target Structure

```text
mx-agent/
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── main.py
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── evals/
│   ├── data/
│   └── log/
└── frontend/
    └── README.md
```

## Backend Migration

Move the current Python project files and runtime-owned backend directories into `backend/`:

- `pyproject.toml`
- `uv.lock`
- `main.py`
- `app/`
- `scripts/`
- `tests/`
- `evals/`
- `data/`
- `log/`

The backend remains a normal `uv` Python project. Developers run backend commands from `backend/`:

```bash
cd backend
uv sync
uv run python main.py
```

Existing imports such as `from app.main import app` and Uvicorn target `app.main:app` remain valid because `backend/` becomes the Python project root.

## Frontend Placeholder

Create `frontend/README.md` explaining that the directory is reserved for the future frontend app. It should not declare a package manager or framework yet.

## Root README

Update the root README to describe the monorepo layout and point backend setup instructions at `backend/`.

Keep the existing detailed backend documentation in the root README for this migration. Only update the top-level project structure and quick-start commands that become incorrect after moving the backend files.

## Path Handling

Runtime paths such as `data/agent_sessions.db`, `data/mx_agent.db`, and `log/mx-agent.log` remain relative paths. Because commands now run from `backend/`, they continue to resolve to backend-owned data and log directories.

Documentation and historical planning directories stay at the repository root:

- `docs/`
- `openspec/`

These describe the whole project rather than only the backend.

## Validation

After migration:

1. `cd backend && uv sync` succeeds.
2. `cd backend && uv run python -c "from app.main import app"` succeeds.
3. `cd backend && uv run python main.py` starts the backend on port 8000.
4. `GET /health`, `GET /info`, and `GET /config` still respond from the running backend.
5. `frontend/README.md` exists and clearly marks the frontend as a placeholder.

## Non-Goals

- Do not create a real frontend implementation.
- Do not introduce npm, pnpm, Vite, React, Next.js, or build tooling.
- Do not rename the Python package from `app`.
- Do not change backend business logic, AgentOS configuration, database schema, or auth behavior.
- Do not rewrite archived docs or historical OpenSpec content.
