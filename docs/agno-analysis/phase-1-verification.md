# Phase 1 Verification

Date: 2026-06-19

## Commands

Backend:

```bash
cd backend
uv run pytest tests/test_os_facade.py -q
uv run pytest tests/test_api.py tests/test_auth.py tests/test_config.py -q
```

Frontend:

```bash
cd frontend
pnpm lint
pnpm build
pnpm start --hostname 127.0.0.1 --port 3002
```

## Results

- `tests/test_os_facade.py`: 4 passed.
- `tests/test_api.py tests/test_auth.py tests/test_config.py`: 15 passed.
- `pnpm lint`: passed.
- `pnpm build`: passed.

## Screenshot Pass

Chrome/CDP viewport: 1512 x 828.

| Page | Reference | Local |
| --- | --- | --- |
| Home | `docs/agno-analysis/reference-screenshots/home.png` | `docs/agno-analysis/local-screenshots/home.png` |
| Chat | `docs/agno-analysis/reference-screenshots/chat.png` | `docs/agno-analysis/local-screenshots/chat.png` |
| Sessions | `docs/agno-analysis/reference-screenshots/sessions.png` | `docs/agno-analysis/local-screenshots/sessions.png` |
| Metrics | `docs/agno-analysis/reference-screenshots/metrics.png` | `docs/agno-analysis/local-screenshots/metrics.png` |

All compared screenshots are 1512 x 828. Phase-one known visual drift remains in product data/content: MX AgentOS uses local enterprise entities and live table rows rather than the public Demo OS sample data and empty-state overlays.

## Interaction Smoke Test

Chrome verified `/chat` on the production build:

- Filled the composer with `测试阶段一聊天交互`.
- Submitted with Enter.
- Verified the user message is rendered.
- Verified the local preview assistant reply is rendered.
- Verified the composer placeholder changes to `Ask a follow-up...`.

Screenshot: `docs/agno-analysis/local-screenshots/chat-interaction.png`.

## Home Workflow Iteration

Chrome/CDP interaction analysis added a Home verification pass:

- Public demo Home renders only Agents, Teams, and Workflows in the main card
  flow.
- Each group initially shows three cards and a `Show more (+N)` command when
  additional entities exist.
- `Show more` expands the group inline and changes to `Show Less`.
- Clicking a group header collapses that group and keeps the rest of the page
  visible.
- `Config` navigates to `/try-demo/config?type=agent&id=sage`, which renders a
  configuration surface with `Open in chat`, `Open docs`, and Agent Details,
  Model, Database, Tools, Sessions, Default Tools, and System Message sections.
- Local `/` now implements the same three-group card flow, collapse/expand,
  Show More/Show Less, Chat links, and `/config` configuration route.

Local Chrome assertions passed for:

- `/` includes Agents, Teams, Workflows, Show More, Chat, and Config controls.
- Interfaces and Operating Systems are no longer rendered in the Home card flow.
- Expanding Agents shows additional agent cards and `Show Less`.
- Collapsing Agents hides agent cards while Teams remains visible.
- `/config?type=agent&id=hr-agent` includes the observed configuration actions
  and sections.

Local screenshots:

- `docs/agno-analysis/local-screenshots/home-list.png`
- `docs/agno-analysis/local-screenshots/home-show-more.png`
- `docs/agno-analysis/local-screenshots/home-agents-collapsed.png`
- `docs/agno-analysis/local-screenshots/home-config.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/home-reference.png`
- `docs/agno-analysis/next-reference-screenshots/home-show-more-reference.png`
- `docs/agno-analysis/next-reference-screenshots/home-agents-collapsed-reference.png`
- `docs/agno-analysis/next-reference-screenshots/home-config-reference.png`

## Chat Inspector Iteration

Chrome/CDP interaction analysis added a second local verification pass for Chat:

- Entity type popover: `Agents`, `Teams`, `Workflows`.
- Entity selector popover: local runnable entities from the selected type.
- Config inspector: right-side panel with Agent Details, Model, Database, Tools, Sessions, Default Tools, and System Message accordions.
- Sessions inspector: right-side panel with `No session found` empty state.
- Prompt pill interaction: clicking `Tell me about Learning Machines` fills the composer.

Local screenshots:

- `docs/agno-analysis/local-screenshots/chat-entity-menu.png`
- `docs/agno-analysis/local-screenshots/chat-config-panel.png`
- `docs/agno-analysis/local-screenshots/chat-sessions-panel.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/chat-shell-state.png`
- `docs/agno-analysis/next-reference-screenshots/chat-config-panel.png`
- `docs/agno-analysis/next-reference-screenshots/chat-sessions-panel.png`

## Chat Deep Link Iteration

Chrome/CDP analysis added the authenticated Agno Chat deep-link verification
for:

`https://os.agno.com/chat?type=team&id=router-team&session=1534cf8b-ec92-40e3-91ed-2fb1e942267c`

Observed Agno behavior:

- The route keeps `type=team`, `id=router-team`, and the session UUID in the
  URL.
- The selected runnable context is `Teams / Router Team`.
- The previous user message is restored as `write insights on ai trends in 200
  words`.
- The assistant run shows a `Finance Agent: Working...` step accordion and an
  answer starting with `Artificial Intelligence (AI) continues to be a
  transformative force in 2024`.
- The composer placeholder remains `Ask anything...`.
- When local AgentOS health checks fail, the page shows `AgentOS not active`,
  `NO TEAMS AVAILABLE`, `LEARN MORE`, `REFRESH`, `EXPLORE A LIVE DEMO AGENTOS`,
  and `Failed to connect to the AgentOS`.

Local Chrome assertions passed for:

- `/chat?type=team&id=router-team&session=1534cf8b-ec92-40e3-91ed-2fb1e942267c`
  preserves the URL and renders `Teams / Router Team`.
- The restored user message, `Finance Agent: Working...`, restored assistant
  answer, inactive overlay, and `Ask anything...` placeholder are visible.

Local screenshots:

- `docs/agno-analysis/local-screenshots/chat-deeplink-restored.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/chat-deeplink-reference.png`

2026-06-19 Chat deep-link follow-up verification:

- `pnpm lint`: passed.
- `pnpm build`: passed.
- Production preview used `pnpm exec next start -p 3003`.

## Production Deployment Iteration

The standalone deployment gap was closed with production container artifacts:

- Root `docker-compose.yml` starts backend FastAPI/AgentOS on port `8000` and
  frontend Next.js standalone on port `3000`.
- `backend/Dockerfile` uses the locked `uv` environment, copies runtime app
  files, exposes `8000`, and starts `uvicorn app.main:app`.
- `frontend/Dockerfile` builds with `pnpm --frozen-lockfile`, uses Next.js
  `output: "standalone"`, copies `.next/static` and `public`, and starts
  `server.js`.
- Root, backend, and frontend `.dockerignore` files exclude local caches,
  runtime data, logs, screenshots, dependencies, and generated build output from
  container contexts.
- README now documents `docker compose up --build`, runtime ports, key
  environment variables, and persisted volumes.

Verification:

- `docker compose config`: passed.
- `pnpm lint`: passed.
- `pnpm build`: passed and emitted `.next/standalone/server.js`.
- `uv run pytest tests/test_os_facade.py -q`: 4 passed.
- `docker compose build`: not executed because the local Docker daemon was not
  running (`Cannot connect to the Docker daemon at unix:///Users/xbjt/.docker/run/docker.sock`).

## Studio And Learning Iteration

Chrome/CDP interaction analysis added Studio and Learning verification passes:

- Studio default route lands on `/try-demo/studio/agents`, showing an Agents
  list with `NEW AGENT`, agent cards, `Current Version 1`, `CHAT`, and `EDIT`.
- `NEW AGENT` opens a full-page builder with Agent Name, Model, Instructions,
  Tools, Database, Basics/Context/Session/Knowledge/Memory/Advanced sections,
  a live right-side summary, and Reset/Save Draft/Publish actions.
- Publish is disabled until required fields are present.
- Learning expands second-level sidebar navigation for User Memories, User
  Profiles, Entity Memories, Session Context, and Decision Logs.
- Learning section pages render a blank/loading workspace with a centered
  three-dot indicator when data is unavailable.
- Local `/studio/agents` now implements the list and builder states.
- Local `/learning/[section]` now implements the observed sidebar subnav and
  loading workspace.

Local Chrome assertions passed for:

- `/studio/agents` includes Agents, New Agent, Current Version 1, Chat, and
  Edit controls.
- Clicking `New Agent` opens the builder with Agent Name, Context Management,
  Save Draft, and a disabled Publish button.
- `/learning/user_memory` includes the expanded Learning subnav and three-dot
  loading state.
- `/learning/decision_log` switches the breadcrumb/active section and keeps the
  three-dot loading state.

Local screenshots:

- `docs/agno-analysis/local-screenshots/studio-list.png`
- `docs/agno-analysis/local-screenshots/studio-new-agent.png`
- `docs/agno-analysis/local-screenshots/learning-user-memory.png`
- `docs/agno-analysis/local-screenshots/learning-decision-log.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/studio-list-reference.png`
- `docs/agno-analysis/next-reference-screenshots/studio-new-agent-reference.png`
- `docs/agno-analysis/next-reference-screenshots/learning-user-memory-reference.png`
- `docs/agno-analysis/next-reference-screenshots/learning-user-profile-reference.png`
- `docs/agno-analysis/next-reference-screenshots/learning-entity-memory-reference.png`

## Data Page Interaction Iteration

Chrome/CDP interaction analysis added a data-page verification pass:

- Table filter popover on `/sessions`.
- Dedicated Sessions console on `/sessions`: Database/Table header, `View`
  radio menu, Session Name and Updated At columns, checkbox selection, URL query
  sync, and page input footer.
- Agno reference row text click did not navigate or open a detail panel; local
  parity now keeps selection in the checkbox column instead of showing a generic
  row inspector.
- Dedicated vertical approvals list on `/approvals`: status radio menu,
  target/date columns, parameter text, pending-only Deny/Approve controls,
  local-safe decision state, and URL query sync.
- `Admin access required` blur overlay matching the public Demo OS gated
  approvals state.

Sessions CDP API findings:

- Initial list request:
  `GET https://demo-os-production-823a.up.railway.app/sessions?page=1&limit=25&sort_by=updated_at&sort_order=desc&db_id=demo-os-db&table=agno_sessions`
- Teams filter request:
  `GET https://demo-os-production-823a.up.railway.app/sessions?page=1&type=team&limit=25&sort_by=updated_at&sort_order=desc&db_id=demo-os-db&table=agno_sessions`

Approvals CDP findings:

- Public demo loads the route and shared auth/config/health requests, but the
  visible approvals list is bundled/static in the gated public state.
- View menu options: Status, All, Pending, Approved, Rejected.
- Selecting Pending updates the route to
  `https://os.agno.com/try-demo/approvals?status=pending&page=1&limit=25`.
- Approve/Deny controls were not clicked on `os.agno.com` because they can
  mutate external Demo OS approval state.

Local screenshots:

- `docs/agno-analysis/local-screenshots/sessions-list.png`
- `docs/agno-analysis/local-screenshots/sessions-filter-menu.png`
- `docs/agno-analysis/local-screenshots/sessions-filter-teams.png`
- `docs/agno-analysis/local-screenshots/sessions-row-selected.png`
- `docs/agno-analysis/local-screenshots/approvals-list.png`
- `docs/agno-analysis/local-screenshots/approvals-filter-menu.png`
- `docs/agno-analysis/local-screenshots/approvals-pending.png`
- `docs/agno-analysis/local-screenshots/approvals-local-decision.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/sessions-reference.png`
- `docs/agno-analysis/next-reference-screenshots/sessions-filter-reference.png`
- `docs/agno-analysis/next-reference-screenshots/sessions-filter-teams-reference.png`
- `docs/agno-analysis/next-reference-screenshots/sessions-row-click-reference.png`
- `docs/agno-analysis/next-reference-screenshots/sessions-sort-reference.png`
- `docs/agno-analysis/next-reference-screenshots/knowledge-table-reference.png`
- `docs/agno-analysis/next-reference-screenshots/approvals-reference.png`
- `docs/agno-analysis/next-reference-screenshots/approvals-filter-reference.png`
- `docs/agno-analysis/next-reference-screenshots/approvals-pending-reference.png`

2026-06-19 Sessions follow-up verification:

- `pnpm lint`: passed.
- `pnpm build`: passed.
- `uv run pytest tests/test_os_facade.py -q`: 4 passed.
- Production preview used `pnpm exec next start -p 3003`.

2026-06-19 Approvals follow-up verification:

- `pnpm lint`: passed.
- `pnpm build`: passed.
- `uv run pytest tests/test_os_facade.py -q`: 4 passed.
- Production preview used `pnpm exec next start -p 3003`.

## Settings Workflow Iteration

Chrome/CDP interaction analysis added a Settings verification pass against the
authenticated Agno OS settings pages:

- Profile: editable name and username fields, disabled email field, disabled
  save state until edits.
- Organization: name form, Pro upgrade panel, members/pending invites tabs,
  member row, and delete organization command.
- OS & Security: AgentOS name/id, copy ID control, protocol selector, endpoint
  input, JWT authorization toggle, security key control, description, tags,
  custom headers, save, and delete AgentOS command.
- Roles: blurred role grid with Enterprise upgrade gate and Learn More/Contact
  Sales actions.
- Billing: Free/Pro/Enterprise pricing columns with current tier and upgrade
  actions.

Local Chrome assertions passed for:

- No local-preview banner in the production shell.
- `/settings/profile` contains Profile, Email, and Save.
- `/settings/organization` contains invite, members, and pending invite states.
- `/settings/os` contains OS & Security, Endpoint URL, Authorization, Security
  key, and Custom headers.
- `/settings/roles` contains the upgrade gate and Contact sales action.
- `/settings/billing` contains Free, Pro, Enterprise, and Current tier.

Local screenshots:

- `docs/agno-analysis/local-screenshots/settings-profile.png`
- `docs/agno-analysis/local-screenshots/settings-organization.png`
- `docs/agno-analysis/local-screenshots/settings-os.png`
- `docs/agno-analysis/local-screenshots/settings-roles.png`
- `docs/agno-analysis/local-screenshots/settings-billing.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/settings-profile-reference.png`
- `docs/agno-analysis/next-reference-screenshots/settings-organization-reference.png`
- `docs/agno-analysis/next-reference-screenshots/settings-os-reference.png`
- `docs/agno-analysis/next-reference-screenshots/settings-roles-reference.png`
- `docs/agno-analysis/next-reference-screenshots/settings-billing-reference.png`

## Traces Explorer Iteration

Chrome/CDP interaction analysis added a Traces verification pass:

- Public demo reference shows `No traces logged` over a blurred trace tree and
  span detail workspace.
- Authenticated reference shows a trace table with Name, Trace ID, Status,
  Duration, Spans, Agent ID, Input, and Created At, plus an AgentOS-not-active
  overlay when the connected OS is down.
- Local `/traces` now renders the observed table columns, a Group by sessions
  filter, Export command, OK/Error status badges, and row click navigation into
  a trace detail explorer.
- Local trace detail includes metadata, Trace Tree, selected span summary,
  Info/Metadata segmented control, Input Text/Formatted segmented control,
  Output Text/Formatted segmented control, copy action, and All Traces back
  action.

Local Chrome assertions passed for:

- `/traces` list includes Trace ID, Agent ID, group-by filter, and local trace
  rows.
- Clicking the first trace row opens detail mode.
- Detail mode includes Trace Tree, Metadata, Input, Output, and All Traces.
- The app shell breadcrumb includes `MX AgentOS / Traces`.

Local screenshots:

- `docs/agno-analysis/local-screenshots/traces-list.png`
- `docs/agno-analysis/local-screenshots/traces-detail.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/traces-list-reference.png`
- `docs/agno-analysis/next-reference-screenshots/traces-authenticated-reference.png`

## Scheduler Workflow Iteration

Chrome/CDP interaction analysis added a Scheduler verification pass:

- Public demo reference shows a `Not available for Demo OS` overlay over a
  blurred scheduler table.
- Authenticated reference can show the Scheduler shell and loading state while
  account/control-plane data resolves.
- Local `/scheduler` now renders a dedicated scheduler table with Enabled
  switches, Name, Cron, Endpoint, Next Run, Updated At, and Run actions.
- Row click opens a schedule details inspector with enabled state, cron,
  endpoint, next run, updated at, Run now, Refresh, and execution-window copy.
- View filter supports All, Enabled, and Disabled schedule states.

Local Chrome assertions passed for:

- `/scheduler` includes the `MX AgentOS / Scheduler` breadcrumb.
- Scheduler table includes Enabled, Cron, Endpoint, and Next Run columns.
- Local schedule rows include daily summary, weekly backup, quarterly
  compliance audit, and customer feedback digest.
- Clicking a row opens the details inspector.
- Enabled filter hides disabled schedule rows while keeping enabled rows.

Local screenshots:

- `docs/agno-analysis/local-screenshots/scheduler-list.png`
- `docs/agno-analysis/local-screenshots/scheduler-detail.png`
- `docs/agno-analysis/local-screenshots/scheduler-filter-enabled.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/scheduler-demo-reference.png`
- `docs/agno-analysis/next-reference-screenshots/scheduler-authenticated-reference.png`

## Evaluation Workflow Iteration

Chrome/CDP interaction analysis added an Evaluation verification pass:

- Public demo reference renders `Evaluation` with database `demo-os-db`, table
  `agno_eval_runs`, `View: All`, disabled `New Eval`, evaluation type/model
  filter, and Updated At sorting.
- Demo evaluation rows include `Agno docs lookup`, `Response quality`,
  `Secret leakage guard`, `Latency baseline`, and `Tool call add_task`.
- The page requests demo data from the AgentOS endpoint at
  `/eval-runs?db_id=demo-os-db&table=agno_eval_runs&page=1&limit=25&sort_by=updated_at&sort_order=desc`.
- Row click opens a right-side details panel with aggregate score tiles,
  Results fields, Delete, ReRun, Close, and Save actions.
- Local `/evaluation` now renders a dedicated evaluation table, scope filter,
  type/model filter, sort toggle, row details inspector, and New Eval creation
  inspector.

Local Chrome assertions passed for:

- `/evaluation` includes five rows and the observed Evaluation Name,
  Agent/Team, Model, Type, and Updated At columns.
- Clicking `Agno docs lookup` opens a details inspector with score tiles,
  Results fields, and Delete/ReRun/Close/Save actions.
- The Performance filter reduces the table to the `Latency baseline` row.
- `New Eval` opens a right-side creation inspector with five inputs.

Local screenshots:

- `docs/agno-analysis/local-screenshots/evaluation-list.png`
- `docs/agno-analysis/local-screenshots/evaluation-detail.png`
- `docs/agno-analysis/local-screenshots/evaluation-filter-performance.png`
- `docs/agno-analysis/local-screenshots/evaluation-new-eval.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/evaluation-reference.png`
- `docs/agno-analysis/next-reference-screenshots/evaluation-row-click-reference.png`

## Memory Workflow Iteration

Chrome/CDP interaction analysis added a Memory verification pass:

- Public demo reference renders `Memory` with database `demo-os-db`, table
  `agno_memories`, Content/Topics/Updated At columns, topic chips, and page
  input `/ 2` pagination.
- Demo data is requested from the AgentOS endpoint at
  `/user_memory_stats?limit=25&page=1&db_id=demo-os-db&table=agno_memories`.
- Rows are display-only table rows; topics render as visible chips plus a `+N`
  overflow chip.
- The empty/help state includes `No memories found`, `Learn more`, and
  `Create memory`.
- `Create memory` opens a centered modal over a blurred workspace with User ID,
  Content, Topics optional, add-tag, Cancel, and Create controls.
- Local `/memory` now renders a dedicated memory table, search control,
  export/create actions, target-like pagination footer, empty state, and
  create-memory dialog with topic entry behavior.

Local Chrome assertions passed for:

- `/memory` includes 10 memory rows and the observed Content, Topics, and
  Updated At columns.
- The first row shows topic chips for Preferences, Notifications, Email, and a
  `+1` overflow chip.
- `Create Memory` opens the modal with the expected fields and disabled add-tag
  state.
- Pressing Enter in the topic field adds a tag and clears the field.
- Searching for a missing token reduces the table to zero rows and shows the
  `No memories found` empty state with actions.

Local screenshots:

- `docs/agno-analysis/local-screenshots/memory-list.png`
- `docs/agno-analysis/local-screenshots/memory-create.png`
- `docs/agno-analysis/local-screenshots/memory-create-topic.png`
- `docs/agno-analysis/local-screenshots/memory-empty-search.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/memory-reference.png`
- `docs/agno-analysis/next-reference-screenshots/memory-create-reference.png`

## Knowledge Workflow Iteration

Chrome/CDP interaction analysis added a Knowledge verification pass:

- Public demo reference renders `Knowledge` with selected collection
  `Clinic Records`, disabled `ADD CONTENT`, Name/Content Type/Metadata/Status/
  Updated At columns, and six clinic-record rows.
- Collection selector opens a popover with collection name plus `Db Id` and
  `Table` metadata for each option.
- Metadata uses uppercase key/value chips and `+N` overflow chips when a row
  has additional metadata.
- Row click opens a right-side edit drawer with Name, Description optional,
  Metadata, Content Type, Status, Updated At, Delete, Cancel, and disabled Save
  controls.
- Local `/knowledge` now renders a dedicated Knowledge table, collection menu,
  disabled Add Content state, sort toggle, metadata overflow chips, and
  reference-style edit drawer.

Local Chrome assertions passed for:

- `/knowledge` includes the observed Name, Content Type, Metadata, Status, and
  Updated At columns.
- Local table includes six clinic-record rows with `COMPLETED` status and
  metadata overflow chips.
- `ADD CONTENT` is disabled to match Demo OS.
- `Clinic Records` opens a collection popover with `Db Id: mx-agent-db` and
  `Table: clinic_records_contents`.
- Clicking `P-1003-care_plan` opens the details drawer with Delete/Cancel/Save;
  Save is disabled before edits.

Local screenshots:

- `docs/agno-analysis/local-screenshots/knowledge-list.png`
- `docs/agno-analysis/local-screenshots/knowledge-collection.png`
- `docs/agno-analysis/local-screenshots/knowledge-detail.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/knowledge-reference.png`
- `docs/agno-analysis/next-reference-screenshots/knowledge-collection-reference.png`
- `docs/agno-analysis/next-reference-screenshots/knowledge-sort-reference.png`

## Metrics Workflow Iteration

Chrome/CDP interaction analysis added a Metrics verification pass:

- Public demo reference renders database `demo-os-db`, table `agno_metrics`,
  `EXPORT`, and month navigation for `JUN 2026`.
- Demo metrics include eight SVG chart panels: Total tokens, Users, Agent Runs,
  Agent Sessions, Team Runs, Team Sessions, Workflow Runs, and Workflow
  Sessions.
- Each chart uses dotted grid texture, day-axis labels, value-axis labels, and
  an export icon.
- Model runs total `688` with `gpt-4o`, `gpt-4.1`, `claude-...`,
  `gpt-4o-...`, `gpt-4.5`, and `Others` percentage rows.
- Demo OS also includes a `Not available for Demo OS` gated notice over a
  blurred chart-like background.
- Local `/metrics` now renders the same eight-chart analytics grid, month
  navigation, export state, selectable charts, model distribution, and gated
  notice.

Local Chrome assertions passed for:

- `/metrics` includes the database/table labels and eight chart SVGs.
- The page includes all observed metric headings and model run rows.
- Previous-month navigation changes `JUN 2026` to `MAY 2026`.
- Export changes to `EXPORTED`.
- Selecting `Team Runs` updates the model section selected metric label.
- The bottom section includes Model runs and the Demo OS unavailable notice.

Local screenshots:

- `docs/agno-analysis/local-screenshots/metrics-grid.png`
- `docs/agno-analysis/local-screenshots/metrics-month-export.png`
- `docs/agno-analysis/local-screenshots/metrics-selected-team-runs.png`
- `docs/agno-analysis/local-screenshots/metrics-bottom.png`

Target reference screenshots:

- `docs/agno-analysis/next-reference-screenshots/metrics-reference.png`
