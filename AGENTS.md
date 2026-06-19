# AGENTS.md

This file gives coding agents project-specific guidance for working in this
repository.

## Project Overview

MX Agent is an enterprise AI assistant for HR, IT, administration, finance, and
legal workflows.

- Backend: FastAPI + Agno AgentOS + SQLAlchemy + SQLite + LanceDB.
- Frontend: Next.js App Router + React + TypeScript + Tailwind CSS v4 +
  shadcn/ui + pnpm.
- Specs and change records live under `openspec/`.
- Project docs live under `docs/`.

## Repository Layout

- `backend/`: FastAPI and Agno backend application.
- `backend/app/agents/`: domain agents and router team.
- `backend/app/tools/`: domain query and action tools.
- `backend/app/models/`: SQLAlchemy data models.
- `backend/app/schemas/`: API and service schemas.
- `backend/app/skills/`: domain knowledge skills and references used by agents.
- `backend/scripts/`: local data, seed, evaluation, and maintenance scripts.
- `backend/tests/`: backend tests.
- `frontend/`: Next.js frontend application.
- `openspec/`: product and architecture specs, proposals, and archived changes.
- `docs/`: supporting documentation and implementation plans.

## Common Commands

Backend:

```bash
cd backend
uv sync
uv run python main.py
uv run pytest
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
pnpm lint
pnpm build
```

Add shadcn/ui components:

```bash
cd frontend
pnpm dlx shadcn@latest add <component>
```

## Backend Guidance

- Keep backend imports rooted at `backend/app` conventions; most commands should
  be run from `backend/`.
- `backend/main.py` starts `app.main:app` on port `8000` with reload enabled.
- The app initializes database tables and knowledge loading during lifespan
  startup.
- Local runtime data belongs under `backend/data/` and logs under `backend/log/`;
  do not commit generated local runtime artifacts.
- Do not commit secrets from `backend/.env`; use `backend/.env.example` for
  documented configuration.

## Frontend Guidance

- `frontend/AGENTS.md` contains additional Next.js-version-specific guidance and
  applies inside the frontend subtree.
- The frontend uses Tailwind CSS v4 and shadcn/ui with `components.json`.
- Prefer shadcn/ui components and local utilities from `@/components` and
  `@/lib` over one-off UI primitives.
- Use `pnpm` for frontend dependency operations. Do not add npm/yarn lockfiles.

## Testing And Verification

- For backend code changes, run the narrow relevant pytest target first, then
  broaden to `uv run pytest` when the change touches shared behavior.
- For frontend changes, run `pnpm lint` and `pnpm build`.
- When touching both frontend and backend integration behavior, verify both
  sides start locally and document any manual checks performed.

## Change Management

- Preserve unrelated worktree changes. This repository may have user changes in
  progress; do not reset, checkout, or clean files unless explicitly requested.
- Keep edits scoped to the requested area.
- For behavior or architecture changes, check `openspec/` and update specs when
  the existing change process calls for it.
- Prefer small, focused commits with descriptive messages.

<!-- CODEGRAPH_START -->
## CodeGraph

This project may have a CodeGraph MCP server (`codegraph_*` tools) configured.
CodeGraph is a tree-sitter-parsed knowledge graph of every symbol, edge, and
file. Reads are sub-millisecond and return structural information grep cannot.

### When to prefer codegraph over native search

Use codegraph for structural questions: what calls what, what would break, where
something is defined, and what a symbol's signature is. Use native grep/read only
for literal text queries such as strings, comments, log messages, or after you
already have a specific file open.

| Question | Tool |
|---|---|
| "Where is X defined?" / "Find symbol named X" | `codegraph_search` |
| "What calls function Y?" | `codegraph_callers` |
| "What does Y call?" | `codegraph_callees` |
| "What would break if I changed Z?" | `codegraph_impact` |
| "Show me Y's signature / source / docstring" | `codegraph_node` |
| "Give me focused context for a task/area" | `codegraph_context` |
| "See several related symbols' source at once" | `codegraph_explore` |
| "What files exist under path/" | `codegraph_files` |
| "Is the index healthy?" | `codegraph_status` |

### Rules of thumb

- Answer directly; do not delegate exploration for architecture or trace
  questions. Use `codegraph_context` first, then one `codegraph_explore` call for
  the source of the surfaced symbols.
- Trust codegraph structural results instead of re-verifying them with grep.
- Do not grep first when looking up a symbol by name.
- Do not chain `codegraph_search` and `codegraph_node` when
  `codegraph_context` is enough.
- Do not loop `codegraph_node` over many symbols; use one capped
  `codegraph_explore` call.
- The index can lag file writes by about 500ms; do not re-query immediately after
  editing a file in the same turn.

### If `.codegraph/` does not exist

Ask the user: "I notice this project doesn't have CodeGraph initialized. Want me
to run `codegraph init -i` to build the index?"
<!-- CODEGRAPH_END -->
