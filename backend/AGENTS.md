# AGENTS.md

This file gives backend-specific guidance for coding agents. It applies to the
`backend/` subtree.

## Backend Overview

The backend is a FastAPI + Agno AgentOS application using SQLAlchemy async
SQLite, LanceDB-backed RAG knowledge, and Langfuse/OpenTelemetry tracing.

## Layout

- `main.py`: local Uvicorn entrypoint for `app.main:app` on port `8000` with
  reload enabled.
- `app/main.py`: FastAPI + AgentOS composition, middleware, exception handlers,
  JWT middleware, lifespan startup, tracing, and route wiring.
- `app/config.py`: Pydantic settings loaded from `backend/.env`.
- `app/api/v1/`: REST endpoints and API router.
- `app/agents/`: domain agents plus the router team.
- `app/core/`: auth, database, middleware, logging, tracing, masking, and
  application exceptions.
- `app/models/`: SQLAlchemy models grouped by `admin`, `finance`, `hr`, `it`,
  and `legal`.
- `app/schemas/`: API/service schemas by domain plus chat, discovery, and error
  response schemas.
- `app/services/`: business services by domain. HR is split into `employee`,
  `manager`, `admin`, and `talent` service modules.
- `app/tools/`: Agno tools by domain, separated into query/action/admin modules.
- `app/skills/`: domain knowledge skills and reference documents used by
  backend agents.
- `app/knowledge/`: RAG knowledge loading and vector store config.
- `app/evals/`: evaluation dataset loading, generation, judging, Langfuse
  integration, publishing, and runner logic.
- `scripts/`: seed, table creation, token generation, knowledge rebuild, and
  evaluation maintenance scripts.
- `evals/datasets/`: evaluation datasets grouped by domain.
- `tests/`: pytest suite for API, auth, config, errors, and evals.

## Commands

```bash
uv sync
uv run python main.py
uv run pytest
```

Useful scripts:

```bash
uv run python scripts/create_tables.py
uv run python scripts/generate_seed.py
uv run python scripts/generate_token.py
uv run python scripts/rebuild_knowledge.py
uv run python scripts/run_evals.py
```

## Guidance

- Use Python `>=3.13` and `uv`; keep `uv.lock` in sync when dependency changes
  are intentional.
- Run backend commands from `backend/` so `.env`, SQLite paths, logs, and
  knowledge directories resolve correctly.
- Keep imports rooted at the backend package, for example `from app.core...`.
- Keep API wiring in `app/api/v1/`, business behavior in `app/services/`, Agno
  tool wrappers in `app/tools/`, and persistence models in `app/models/`.
- When adding or renaming models, tools, services, or schemas, update the
  relevant package `__init__.py` exports if the surrounding domain uses them.
- The backend lifespan initializes logging, database tables, and knowledge
  loading. Be careful with changes that make startup perform network calls or
  mutate local data unexpectedly.
- Do not commit secrets from `.env`; use `.env.example` for documented
  configuration.

## Data And Generated Files

- Local runtime data belongs under `data/`, including SQLite databases and
  LanceDB vector data.
- Local logs belong under `log/`.
- Do not commit generated caches or runtime artifacts such as `__pycache__/`,
  `.pytest_cache/`, `.venv/`, `data/`, or `log/`.
- Knowledge source documents live under `data/knowledge/docs/` at runtime. Treat
  generated vector data under `data/knowledge/lancedb/` as local runtime state.

## Testing

- Run the narrow relevant pytest target first, then broaden to `uv run pytest`
  when shared behavior, startup, auth, evals, or core services are touched.
- For evaluation changes, run focused tests under `tests/test_eval_*.py` and the
  relevant script in `scripts/` when practical.
