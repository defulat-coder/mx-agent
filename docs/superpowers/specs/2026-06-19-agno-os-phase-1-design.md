# Agno OS Phase 1 Product Design

## Goal

Build the first production-grade slice of an Agno OS-parity product inside this repository: a deployable MX AgentOS console with a high-fidelity app shell, core navigation pages, and a working chat loop backed by the existing FastAPI + Agno AgentOS backend.

This phase does not complete full Agno OS parity. It establishes the product shell, stable backend facade, visual baseline, and verification workflow needed to iterate page by page toward the full goal.

## Evidence

Reference analysis lives in `docs/agno-analysis/page-inventory.md`.

Reference screenshots were captured from the public Agno Demo OS at a 1512 x 828 viewport:

- `docs/agno-analysis/reference-screenshots/home.png`
- `docs/agno-analysis/reference-screenshots/chat.png`
- `docs/agno-analysis/reference-screenshots/sessions.png`
- `docs/agno-analysis/reference-screenshots/traces.png`
- `docs/agno-analysis/reference-screenshots/memory.png`
- `docs/agno-analysis/reference-screenshots/knowledge.png`
- `docs/agno-analysis/reference-screenshots/metrics.png`
- `docs/agno-analysis/reference-screenshots/approvals.png`
- `docs/agno-analysis/reference-screenshots/scheduler.png`

The local backend already exposes an Agno AgentOS app through `agent_os.get_app()` and a stable product chat facade at `POST /v1/chat`.

## Product Scope

Phase 1 includes:

- Agno-style app shell with fixed sidebar, top OS bar, command buttons, status indicators, footer links, and responsive behavior.
- Home workspace with Agents, Teams, Workflows, Interfaces, and OS cards.
- Chat page with entity selector, starter prompts, session actions, bottom composer, and live calls to `POST /v1/chat`.
- Runtime data pages for Sessions, Traces, Memory, Knowledge, Metrics, Evaluation, Approvals, and Scheduler.
- Basic Settings shell with Profile and OS & Security surfaces represented enough to preserve navigation and future integration points.
- Screenshot-based visual verification against the captured reference pages.

Phase 1 does not include:

- Billing checkout, paid-plan enforcement, or external sales flows.
- Real organization invitations, email delivery, or SSO.
- Slack, WhatsApp, or other external interface integrations.
- Full custom role management.
- A dependency on hosted `os.agno.com` at runtime.

## Architecture

### Frontend

The Next.js frontend becomes the primary product UI.

Routes:

- `/`
- `/chat`
- `/sessions`
- `/traces`
- `/memory`
- `/knowledge`
- `/metrics`
- `/evaluation`
- `/approvals`
- `/scheduler`
- `/settings/profile`
- `/settings/organization`
- `/settings/os`
- `/settings/roles`
- `/settings/billing`

Core UI modules:

- App shell: sidebar, topbar, breadcrumb/OS selector, support and refresh actions.
- Navigation model: route definitions, active state, collapsible groups for Studio, Learning, and Settings.
- Entity cards: agents, teams, workflows, interfaces, operating systems.
- Data table: sticky header, mono headers, compact rows, sorting controls, empty states.
- Chat: message list, starter prompts, composer, send action, response rendering, loading/error states.
- Status and gated states: active/inactive OS, Demo-like warning, unavailable feature, admin-only feature.
- Form primitives for profile and OS settings.

The visual thesis is a quiet operational console: white workspace, fine zinc borders, orange-red brand accent, compact mono command controls, and dense but readable tables.

### Backend

Add a stable MX OS facade under `/v1/os/*`. The facade shields the frontend from direct Agno internal response shapes while still using the existing AgentOS runtime where practical.

Initial endpoints:

- `GET /v1/os/overview`
- `GET /v1/os/entities`
- `GET /v1/os/sessions`
- `GET /v1/os/traces`
- `GET /v1/os/memory`
- `GET /v1/os/knowledge`
- `GET /v1/os/metrics`
- `GET /v1/os/evaluations`
- `GET /v1/os/approvals`
- `GET /v1/os/schedules`
- `GET /v1/os/settings`

`POST /v1/chat` remains the chat execution endpoint. The frontend should treat `reply`, `action`, and `session_id` as the stable chat contract.

For pages where AgentOS runtime data is not yet exposed in a convenient local shape, the facade returns deterministic seeded data derived from the Agno reference inventory. Seed data must be clearly owned by the local app and should not include personal account data from browser analysis.

### Data Flow

1. App shell loads `GET /v1/os/overview` for current OS status, navigation badges, and user/workspace metadata.
2. Each page loads its own `/v1/os/*` endpoint.
3. Chat sends messages through `POST /v1/chat`.
4. Successful chat responses update the local session view with the returned `session_id`.
5. Refresh controls revalidate the current page endpoint, not the full app.

## Page Behavior

### Home

Render grouped sections for Agents, Teams, Workflows, Interfaces, and All OSes.

Required interactions:

- Collapse/expand each group.
- Show More reveals hidden cards in that group.
- Chat buttons navigate to `/chat?type=<entity-type>&id=<entity-id>`.
- Config buttons navigate to future configuration views or show an explicit Phase 1 unavailable state.

### Chat

Render the selected entity, empty session starter prompts, session actions, and composer.

Required interactions:

- Selecting a starter prompt fills or sends through the composer.
- Sending a message calls `POST /v1/chat`.
- Loading state is visible while the backend is running.
- Errors render inline without clearing user input.
- Missing or inactive entity disables send and explains why.

### Data Pages

Sessions, Traces, Memory, Knowledge, Evaluation, Approvals, and Scheduler share table primitives.

Required interactions:

- Page-specific table columns match the inventory.
- Sort/filter controls update URL query params.
- Row selection opens a detail panel or page-specific detail section when enough data exists.
- Empty and unavailable states match the Agno tone and spacing.

### Metrics

Render compact metric cards and chart-like panels.

Required interactions:

- Month navigation updates displayed period.
- Export action exists as a visible disabled or no-op Phase 1 command with clear state.

### Settings

Profile and OS & Security get first-class form layouts. Organization, Roles, and Billing can initially render high-fidelity read-only/gated surfaces.

Required interactions:

- Profile fields render with disabled email.
- OS & Security shows endpoint URL, auth/security key sections, tags, custom headers, and danger zone structure.
- Save actions are present but may return local validation-only Phase 1 feedback unless a backend update endpoint is implemented in the same slice.

## Error Handling

- Network failures show a small inline error area in the page body and keep the app shell usable.
- Chat failures preserve the composer text and session context.
- Backend facade errors return the repository's existing structured error format where possible.
- Missing runtime data should not blank a page; use explicit empty states.

## Verification

Backend:

- Add pytest coverage for `/v1/os/*` response contracts.
- Keep existing `/v1/chat` tests passing.
- Run focused backend tests first, then broaden to `uv run pytest` if the facade touches shared auth or routing.

Frontend:

- Run `pnpm lint`.
- Run `pnpm build`.
- Start local frontend and capture screenshots for at least:
  - Home
  - Chat
  - Traces
  - Memory
  - Knowledge
  - Metrics
  - Approvals
  - Scheduler
  - Sessions
- Compare local screenshots against `docs/agno-analysis/reference-screenshots/*.png` at the 1512 x 828 viewport.
- Verify a mobile viewport for no overlapping text, no broken tables, and accessible sidebar navigation.

Deployment:

- Backend and frontend must be runnable independently with the documented commands in `AGENTS.md`.
- The final implementation must not require access to `os.agno.com`.

## Implementation Notes

- The root README currently lags the actual repository state by describing `frontend/` as a placeholder. The implementation plan should include a documentation update.
- The latest main branch split `backend/app/services/hr.py` into the `backend/app/services/hr/` package. New backend code should import through existing stable package exports where possible.
- CodeGraph is not initialized in this worktree. Structural code exploration should use native search until the index is initialized.

## Open Questions For Later Phases

- Which local AgentOS native endpoints should become public product API contracts versus internal implementation details?
- Should traces and metrics be sourced from Agno's SQLite session database, Langfuse, or a local MX-specific aggregation table?
- Which settings operations should be writable in Phase 2: OS endpoint/security keys, profile, organization, roles, or billing?
