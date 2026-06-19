# Agno OS Reference Inventory

Source: Chrome/CDP read-only analysis of `https://os.agno.com` on 2026-06-19.

## Reference Screenshots

All screenshots were captured from the public Demo OS surface at a 1512 x 828 viewport.

| Page | URL | Screenshot |
|---|---|---|
| Home | `https://os.agno.com/try-demo` | `docs/agno-analysis/reference-screenshots/home.png` |
| Chat | `https://os.agno.com/try-demo/chat?type=agent` | `docs/agno-analysis/reference-screenshots/chat.png` |
| Sessions | `https://os.agno.com/try-demo/sessions?sort_by=updated_at_desc&type=all&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/sessions.png` |
| Traces | `https://os.agno.com/try-demo/traces?group_by=sessions&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/traces.png` |
| Memory | `https://os.agno.com/try-demo/memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/memory.png` |
| Knowledge | `https://os.agno.com/try-demo/knowledge?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/knowledge.png` |
| Metrics | `https://os.agno.com/try-demo/metrics` | `docs/agno-analysis/reference-screenshots/metrics.png` |
| Approvals | `https://os.agno.com/try-demo/approvals?status=all&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/approvals.png` |
| Scheduler | `https://os.agno.com/try-demo/scheduler` | `docs/agno-analysis/reference-screenshots/scheduler.png` |

## Application Shell

- Layout: fixed left sidebar around 208px wide, main workspace to the right.
- Top bar: 56px workspace header, breadcrumb/current OS selector on the left, support and refresh controls on the right.
- Demo mode: a 40px gray banner sits above the app shell with "WHAT IS DEMO OS?" and "LEAVE DEMO OS".
- Sidebar sections: Home, Chat, Sessions, Traces, Studio, Learning, Memory, Knowledge, Metrics, Evaluation, Approvals, Scheduler, Settings.
- Sidebar footer: docs, Discord, GitHub links and compact user display.
- Visual system: Inter for text, DM Mono for uppercase command buttons, white canvas, light zinc borders, orange-red brand accent, tight 8-16px spacing.

## Page Inventory

### Home

- Groups: Agents, Teams, Workflows, Interfaces, All OSes.
- Main interactions: accordion collapse/expand, Chat buttons, Config buttons, Show More controls, OS switch/edit/delete controls.
- Card pattern: red square icon, title, description, mono tag chips, command buttons in footer.

### Chat

- Main modes: agent/team/workflow selection inferred from `type` query param.
- Empty state: entity selector, See Config, Sessions, New Session, starter prompt suggestions.
- Active session state: centered conversation column, assistant step accordion, markdown response, copy action, bottom sticky composer.
- Composer: textarea, attachment/settings icon buttons, entity selector, send button. Disabled when no runnable entity or OS inactive.

### Sessions

- Header context: database and table labels.
- Controls: View filter, export, sort by Updated At.
- Table columns: Session Name, Updated At.
- Row click likely navigates to session detail/chat.

### Traces

- Default demo detail view includes trace metadata, trace tree, input, output, spans, and timing.
- List/table mode uses columns: Name, Status, Duration, Spans, Agent/Team/Workflow, Input, Created At.
- Interaction pattern: grouped-by sessions query param, trace tree expansion, span detail selection.

### Memory

- Header context: database and `agno_memories` table.
- Controls: create memory, sort by Updated At.
- Table columns: Content, Topics, Updated At.
- Row content uses topic chips and compact timestamps.

### Knowledge

- Header context: knowledge source selector, selected collection such as Clinic Records.
- Controls: Add Content, sort by Updated At.
- Table columns: Name, Content Type, Metadata, Status, Updated At.
- Metadata uses key/value chips; statuses include Completed/Processing.

### Metrics

- Header context: database and `agno_metrics` table.
- Controls: export, month navigation.
- Main content: metric chart grid for tokens, users, agent/team/workflow runs and sessions.
- Secondary content: model run distribution and gated Demo OS empty/upgrade notice for unavailable data.

### Evaluation

- Header context: database and `agno_eval_runs` table.
- Controls: View filters, New Eval, evaluation type filter, sort by Updated At.
- Table columns: Evaluation Name, Agent/Team, Model, Type, Updated At.

### Approvals

- Header: Approvals with View filter.
- Content: approval cards/list items with tool/action name, requester agent/team/workflow, date, parameters, Deny and Approve actions.
- Demo state overlays admin access required messaging for management.

### Scheduler

- Header: Scheduler.
- Table columns: Enabled, Name, Cron, Endpoint, Next Run, Updated At.
- Rows use switches for enable state and cron/endpoint monospace content.
- Demo state includes not-available messaging.

### Settings

- Settings pages observed outside public demo:
  - Profile: name, username, disabled email, save.
  - Organization: organization name, invite/pro upgrade panel, members, pending invites, danger zone.
  - OS & Security: OS name/id, endpoint URL protocol selector, JWT authorization, security key, description, tags, custom headers, danger zone, save.
  - Roles: built-in roles and upgrade gate for custom role management.
  - Billing: Free/Pro/Enterprise pricing columns and upgrade actions.

## Observed API Shape

Agno OS frontend uses `https://os-api.agno.com/api/v1` for hosted account/control-plane data:

- `POST /auth/authenticate`
- `GET /auth/authrefresh`
- `GET /auth/demo-sdk-token`
- `GET /users/me`
- `GET /users/me/organizations`
- `GET /org/`
- `GET /org/billing/`
- `GET /org/roles/?include_scopes=true`
- `GET /org/memberships?statuses=active&limit=10&offset=0`
- `GET /org/invitations?invitation_state=pending&limit=10&offset=0`
- `GET /operating-systems/`
- `GET /operating-systems/{id}/security-keys`

The page also connects to a local AgentOS endpoint configured on the OS record. When the local AgentOS is unreachable, the workspace still renders cached/demo content but overlays an "AgentOS not active" panel.

## Local Repository Mapping

- Existing backend already exposes Agno AgentOS routes through `agent_os.get_app()`.
- Existing backend stable product facade: `POST /v1/chat`.
- Existing backend AgentOS routes excluded from JWT middleware include agents, teams, sessions, memories, knowledge, traces, metrics, config, eval-runs, and related runtime endpoints.
- Existing frontend is a minimal Next.js shell and can be replaced by the Agno-style app surface.

## Open Verification Items

- Exact request/response bodies for chat runs and streaming behavior.
- Whether local AgentOS routes provide enough data for traces, memories, knowledge, metrics, evals, approvals, and scheduler, or whether MX-specific facade endpoints are needed.
- Mobile responsive behavior for sidebar, composer, data tables, and detail panels.
- Pixel-diff tolerance and viewport matrix for final 1:1 screenshot verification.
