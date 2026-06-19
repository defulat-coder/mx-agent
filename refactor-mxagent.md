# MX Agent Refactor Log

Date: 2026-06-19

## Goal

Refactor MX Agent until the architecture is in a satisfactory state. After each
significant step:

- run live verification,
- perform an autoreview,
- commit the completed step,
- record the outcome here.

## Constraints

- Preserve unrelated worktree changes.
- Avoid committing generated runtime data, secrets, caches, or local artifacts.
- Backend verification starts with focused pytest targets, then broadens when a
  change touches shared behavior.
- Frontend verification uses `pnpm lint` and `pnpm build` for frontend changes.
- CodeGraph is configured in instructions but not initialized in this checkout,
  so structural exploration starts with repository files and tests unless the
  index is built later.

## Baseline

- Branch: `codex/monorepo-migration`
- Existing untracked path before this work: `.codex/`
- Initial project shape:
  - Backend: FastAPI/Agno app under `backend/app`
  - Frontend: Next.js app under `frontend`
  - Specs: `openspec/`
  - Existing design and plan docs: `docs/superpowers/`

## Progress

### Step 0 - Baseline and orientation

Status: completed

Verification:

- Backend baseline before fixes: `uv run pytest` -> 92 passed, 10 failed.
- Frontend baseline: `pnpm lint` -> passed.
- Frontend baseline: `pnpm build` -> passed.

Notes:

- Root domain docs such as `CONTEXT.md` and `docs/adr/` are not present yet.
  Existing domain and architecture vocabulary will be taken from `AGENTS.md`,
  `docs/`, and `openspec/`.
- Backend failures were concentrated in stale API/auth/config expectations after
  the AgentOS and monorepo migration: missing `/v1/chat`, `/health` expecting
  old 404 behavior, AgentOS auth error shape, and SQLite replacing the old
  PostgreSQL default.

### Step 1 - Restore stable chat API facade

Status: completed

Architecture change:

- Added a product-level `POST /v1/chat` facade over the AgentOS `router_team`.
- Added `ChatRequest` and `ChatResponse` schemas so external clients keep a
  stable API that does not expose AgentOS route internals.
- Decoded JWT claims in the chat facade and converted them to AgentOS
  `session_state`, keeping tool-layer identity checks intact.
- Excluded `/v1/chat` from AgentOS `JWTMiddleware` so the project-level unified
  error response remains consistent for this product endpoint.
- Updated API/config tests to match the current AgentOS runtime and SQLite
  backend defaults.

Verification:

- Focused tests: `uv run pytest tests/test_api.py tests/test_auth.py tests/test_config.py`
  -> 14 passed.
- Full backend suite: `uv run pytest` -> 102 passed.
- Live HTTP check on port 8001:
  - `GET /health` -> 200 with `X-Request-ID` and `X-Trace-Id`.
  - `POST /v1/chat` without token -> 401 with `code=40101`.
  - `POST /v1/chat` with invalid token -> 401 with `code=40103`.

Autoreview:

- The facade is intentionally thin: request validation, JWT-to-session-state
  adaptation, and AgentOS output normalization only.
- Tests mock the team call so API contract coverage does not depend on live LLM
  credentials.
- Known remaining issue: chat facade auth duplicates part of AgentOS JWT
  validation. This is acceptable for now because it preserves the product API's
  unified error response; a later deepening pass can extract a shared JWT claims
  adapter.
