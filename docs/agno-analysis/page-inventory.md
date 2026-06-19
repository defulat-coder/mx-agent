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
| Studio | `https://os.agno.com/try-demo/studio/agents` | `docs/agno-analysis/next-reference-screenshots/studio-list-reference.png` |
| Learning | `https://os.agno.com/learning/user_memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-user-memory-reference.png` |
| Memory | `https://os.agno.com/try-demo/memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/memory.png` |
| Knowledge | `https://os.agno.com/try-demo/knowledge?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/knowledge.png` |
| Metrics | `https://os.agno.com/try-demo/metrics` | `docs/agno-analysis/reference-screenshots/metrics.png` |
| Approvals | `https://os.agno.com/try-demo/approvals?status=all&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/approvals.png` |
| Scheduler | `https://os.agno.com/try-demo/scheduler` | `docs/agno-analysis/reference-screenshots/scheduler.png` |

## Application Shell

- Layout: fixed left sidebar around 208px wide, main workspace to the right.
- Top bar: 56px workspace header, breadcrumb/current OS selector on the left, support and refresh controls on the right.
- Demo mode: public `/try-demo` pages can show a gray demo banner; authenticated
  Settings pages render without that banner and use the app shell directly.
- Sidebar sections: Home, Chat, Sessions, Traces, Studio, Learning, Memory, Knowledge, Metrics, Evaluation, Approvals, Scheduler, Settings.
- Sidebar footer: docs, Discord, GitHub links and compact user display.
- Visual system: Inter for text, DM Mono for uppercase command buttons, white canvas, light zinc borders, orange-red brand accent, tight 8-16px spacing.

## Page Inventory

### Home

- Groups: Agents, Teams, and Workflows. Interfaces and operating systems are
  managed elsewhere in the shell rather than rendered in the public Demo OS Home
  card flow.
- Card pattern: red square icon, title, description, mono tag chips with `+N`
  overflow chips, and command buttons in a tinted footer.
- Interaction pass on 2026-06-19:
  - Initial Home shows three cards per group and `Show more (+N)` controls.
  - Agents sample rows include `Sage`, `Voyager`, and `Ledger`; Teams include
    `Dash`, `Mentor`, and `Clinic`; Workflows include `Daily Brief`,
    `AI Digest`, and `Scribe`.
  - Clicking `Show more (+6)` expands the Agents group inline and changes the
    control to `Show Less`.
  - Clicking the group header collapses that group, leaving only the uppercase
    section title while subsequent groups stay visible.
  - Card `Config` navigates to `/try-demo/config?type=agent&id=sage` and renders
    a configuration surface with `Open in chat`, `Open docs`, and accordion
    rows for Agent Details, Model, Database, Tools, Sessions, Default Tools, and
    System Message.
  - Local implementation now follows the three-group Home card flow, supports
    collapse/expand, Show More/Show Less, Chat links, and a local `/config`
    page with the observed configuration sections.

### Studio

- Default route redirects to `/try-demo/studio/agents`.
- Agents list shows an uppercase count such as `1 AGENTS`, a `NEW AGENT`
  command, and agent cards with name, `Current Version 1`, `CHAT`, and `EDIT`.
- `NEW AGENT` opens a full-page builder rather than a modal. The page title is
  `New Agent` and the top breadcrumb/action reads `Agents`.
- Builder form fields: Agent Name, Model select, Instructions optional, Tools
  optional selector, and Database optional selector. Demo OS auto-selects the
  database.
- Builder sections: Basics, Context Management, Session State, Knowledge,
  Memory, and Advanced.
- Right side shows a live configuration summary headed by `Name of agent` and a
  section summary such as Basics.
- Footer actions are `RESET`, `SAVE DRAFT`, and `PUBLISH`; Publish is disabled
  until required data is present.
- Local implementation now adds `/studio/agents`, sidebar Studio sub-navigation,
  agent cards, New Agent/Edit builder states, form preview, draft save state,
  and disabled Publish parity.

### Learning

- Default route redirects to `/learning/user_memory`.
- Learning expands the sidebar with second-level navigation: User Memories, User
  Profiles, Entity Memories, Session Context, and Decision Logs.
- The main header breadcrumb shows the active section, while the content area is
  an empty/loading workspace with a centered three-dot indicator when the data
  surface is unavailable.
- Local implementation now adds `/learning/[section]`, the sidebar subnav, and
  reference-style blank/loading states for User Memories and Decision Logs.

### Chat

- Main modes: agent/team/workflow selection inferred from `type` query param.
- Empty state: entity selector, See Config, Sessions, New Session, starter prompt suggestions.
- Active session state: centered conversation column, assistant step accordion, markdown response, copy action, bottom sticky composer.
- Composer: textarea, attachment/settings icon buttons, entity selector, send button. Disabled when no runnable entity or OS inactive.
- Interaction pass on 2026-06-19:
  - Breadcrumb type selector opens a compact popover with `Agents`, `Teams`, `Workflows`.
  - Breadcrumb entity selector opens a 200px popover with runnable entity names such as `Sage`, `Voyager`, `Ledger`.
  - `SEE CONFIG` opens a right-side inspector around 500px wide; the chat canvas shrinks left rather than opening a modal.
  - The configuration inspector title is `{Entity}'s Configuration` and uses accordion rows: Agent Details, Model, Database, Tools, Sessions, Default Tools, System Message.
  - When any inspector is open, text controls collapse to icon buttons for config/session history plus `NEW SESSION`.
  - `SESSIONS` opens the same right-side inspector area with `Sessions`, close control, and an empty state: `No session found` plus `No session records yet. Start a conversation to create one.`
  - Starter prompt pills fill the composer, while `NEW SESSION` resets the conversation state.

### Sessions

- Header context: database and table labels.
- Controls: View filter, export, sort by Updated At.
- Table columns: Session Name, Updated At.
- Row click likely navigates to session detail/chat.
- Local parity iteration on 2026-06-19 added a row inspector pattern for table pages: clicking a row selects it, checks the row box, and opens a right-side details panel while preserving the table workspace.

### Traces

- Public demo state can show a `No traces logged` overlay while preserving a
  blurred trace-detail surface behind it.
- Authenticated/account state can show an inactive-AgentOS overlay over the
  traces table when the connected AgentOS is unreachable.
- List/table mode uses columns: Name, Trace ID, Status, Duration, Spans,
  Agent ID, Input, Created At.
- Detail mode includes trace metadata, trace tree, selected span summary,
  Info/Metadata segment, Input Text/Formatted segment, Output Text/Formatted
  segment, copy action, and an All Traces back action.
- Interaction pattern: grouped-by sessions query param, trace row selection,
  trace tree span selection, and segmented content switching.
- Interaction pass on 2026-06-19:
  - `https://os.agno.com/try-demo/traces?group_by=sessions&page=1&limit=25`
    exposes the demo empty-state overlay plus underlying tree/detail layout.
  - `https://os.agno.com/traces?group_by=sessions&page=1&limit=25` exposes
    account trace rows and an AgentOS-not-active overlay when the OS endpoint is
    down.
  - Local implementation keeps the list operational, uses the observed trace
    columns, and opens a functional trace detail explorer on row click.

### Memory

- Header context: database and `agno_memories` table.
- Controls: create memory, sort by Updated At.
- Table columns: Content, Topics, Updated At.
- Row content uses topic chips and compact timestamps.
- Interaction pass on 2026-06-19:
  - Demo OS requests memory rows from
    `/user_memory_stats?limit=25&page=1&db_id=demo-os-db&table=agno_memories`
    on the configured AgentOS endpoint after fetching the demo SDK token.
  - Memory rows are non-navigating table rows with `cursor-default`; the table
    uses a 50/30/20 column split for Content, Topics, and Updated At.
  - Topic chips are lowercase in data and uppercase visually, showing the first
    three topics plus a `+N` chip for hidden topics.
  - Pagination appears at the bottom as a page input and `/ 2` total marker.
  - The empty/help state reads `No memories found`, includes short copy, and
    provides `Learn more` and `Create memory` actions.
  - `Create memory` opens a centered modal over a blurred page with `User ID`,
    `Content`, `Topics optional`, disabled add-tag control until input, and
    `Cancel`/`Create` actions.
  - Local implementation now follows the dedicated memory table geometry, topic
    chip truncation, search/empty state, pagination footer, and create-memory
    dialog.

### Knowledge

- Header context: knowledge source selector, selected collection such as Clinic Records.
- Controls: Add Content, sort by Updated At.
- Table columns: Name, Content Type, Metadata, Status, Updated At.
- Metadata uses key/value chips; statuses include Completed/Processing.
- Interaction pass on 2026-06-19:
  - Public Demo OS renders `Knowledge`, collection selector `Clinic Records`,
    disabled `ADD CONTENT`, and an `Updated at` sort control.
  - Demo rows are loaded for `clinic_records_contents` and include
    `P-1002-care_plan`, `P-1003-bloodwork`, `P-1003-care_plan`,
    `P-1001-bloodwork`, `P-1001-visit_note`, and `P-1002-bloodwork`.
  - Collection selector opens a compact popover with entries such as
    `Clinic Records`, `Dash Knowledge`, `Dash Learnings`,
    `Investment Knowledge`, `Investment Learnings`, and `Coach Learnings`.
    Each entry shows `Db Id` and `Table` metadata.
  - Metadata renders as uppercase key/value chips, showing the first metadata
    key and a `+N` overflow chip for hidden metadata.
  - Row click opens a right-side edit drawer with Name, Description optional,
    Metadata, Content Type, Updated At, and Delete/Cancel/Save actions. Save is
    disabled until edits.
  - Local implementation now uses a dedicated Knowledge panel with the observed
    collection menu, disabled Add Content state, table geometry, metadata
    overflow chips, sort toggle, and right-side edit drawer.

### Metrics

- Header context: database and `agno_metrics` table.
- Controls: export, month navigation.
- Main content: metric chart grid for tokens, users, agent/team/workflow runs and sessions.
- Secondary content: model run distribution and gated Demo OS empty/upgrade notice for unavailable data.
- Interaction pass on 2026-06-19:
  - Demo OS shows database `demo-os-db`, table `agno_metrics`, `EXPORT`, and
    month navigation with previous enabled and next disabled while viewing
    `JUN 2026`.
  - The chart grid includes eight time series: Total tokens, Users, Agent Runs,
    Agent Sessions, Team Runs, Team Sessions, Workflow Runs, and Workflow
    Sessions.
  - Metrics uses SVG-based line charts with dotted grid backgrounds, axis labels
    at days 1/8/15/22/29, and per-chart export icon controls.
  - Model runs totals `688` and lists `gpt-4o`, `gpt-4.1`, `claude-...`,
    `gpt-4o-...`, `gpt-4.5`, and `Others` with percentage shares.
  - Demo OS renders a `Not available for Demo OS` gated notice over a blurred
    chart-like background for unavailable analytics.
  - Local implementation now renders the eight-chart grid, month navigation,
    export state, selectable metric charts, model run distribution, and gated
    notice.

### Evaluation

- Header context: database and `agno_eval_runs` table.
- Controls: View filters, New Eval, evaluation type filter, sort by Updated At.
- Table columns: Evaluation Name, Agent/Team, Model, Type, Updated At.
- Interaction pass on 2026-06-19:
  - Demo OS requests evaluation runs from
    `/eval-runs?db_id=demo-os-db&table=agno_eval_runs&page=1&limit=25&sort_by=updated_at&sort_order=desc`
    on the configured AgentOS endpoint after fetching the demo SDK token.
  - Demo table rows include `Agno docs lookup`, `Response quality`,
    `Secret leakage guard`, `Latency baseline`, and `Tool call add_task`.
  - `NEW EVAL` is visible but disabled in Demo OS.
  - The first View menu filters by `All`, `Agents`, and `Teams`; the second
    View menu groups `Types` (`Accuracy`, `Performance`, `Reliability`,
    `Agent as Judge`) and `Models` (`gpt-5.5`).
  - Row click opens a right-side evaluation details panel with aggregate score
    tiles, result fields (`Score`, `Output`, `Expected Output`, `Input`,
    `Reason`), and `Delete`, `ReRun`, `Close`, `Save` actions.
  - Local implementation preserves the table controls, implements type/scope
    filtering, makes `NEW EVAL` open a creation inspector, and adds a functional
    run-detail inspector.

### Approvals

- Header: Approvals with View filter.
- Content: approval cards/list items with tool/action name, requester agent/team/workflow, date, parameters, Deny and Approve actions.
- Demo state overlays admin access required messaging for management.
- Public demo renders approvals as a vertical list rather than a database table: action name on the left, agent/team target and date on the right, params below, and Deny/Approve controls on pending items.
- Local implementation follows that vertical approval list and keeps an `Admin access required` overlay on top, matching the demo's gated management state.

### Scheduler

- Header: Scheduler.
- Table columns: Enabled, Name, Cron, Endpoint, Next Run, Updated At.
- Rows use switches for enable state and cron/endpoint monospace content.
- Demo state includes not-available messaging.
- Interaction pass on 2026-06-19:
  - Public demo eventually resolves to a `Not available for Demo OS` overlay on
    top of a blurred schedule table.
  - Authenticated/account state can remain in a loading state when the connected
    AgentOS scheduler data is unavailable.
  - Underlying table rows include switch controls, schedule name, cron string,
    endpoint path, next run timestamp, and updated-at timestamp.
  - Local implementation keeps the schedule table usable, adds View filters for
    all/enabled/disabled, preserves the switch-first row layout, supports Run
    actions, and opens a right-side schedule details inspector.

### Settings

- Settings pages observed outside public demo:
  - Profile: name, username, disabled email, save.
  - Organization: organization name, invite/pro upgrade panel, members, pending invites, danger zone.
  - OS & Security: OS name/id, endpoint URL protocol selector, JWT authorization, security key, description, tags, custom headers, danger zone, save.
  - Roles: built-in roles and upgrade gate for custom role management.
  - Billing: Free/Pro/Enterprise pricing columns and upgrade actions.
- Interaction pass on 2026-06-19:
  - Settings sub-navigation is rendered under the sidebar Settings item:
    `Profile`, `Organization`, `OS & Security`, `Roles`, `Billing`.
  - Profile uses a sparse form: `NAME`, `USER NAME`, disabled `EMAIL`, and a
    disabled `SAVE` button until edits are made.
  - Organization uses the same sparse form top section, then a bordered Pro
    upgrade panel for multi-user access, tab-like `Members` and
    `Pending invites` counters, member rows, and `DELETE ORGANIZATION`.
  - OS & Security is a long form with a disabled ID + copy control, protocol
    select plus endpoint input, collapsible-looking authorization section,
    JWT toggle, security key generation control, additional settings,
    description textarea, tag entry, custom header key/value inputs, `SAVE`,
    and `DELETE AGENTOS`.
  - Roles shows role tiles with `MANAGE` and `DELETE` actions behind a blurred
    Enterprise upgrade gate. The foreground callout has `LEARN MORE` and
    `CONTACT SALES`.
  - Billing shows three equal-height pricing columns: Free/current tier, Pro
    at `$150 per month`, and Enterprise/contact us.
  - Settings page requests observed through CDP: `/auth/authenticate`,
    `/org/`, `/users/me`, `/users/me/organizations`, `/operating-systems/`,
    `/operating-systems/{id}/security-keys`, `/org/billing/`,
    `/org/memberships`, `/org/invitations`, and
    `/org/roles/?include_scopes=true`.

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
