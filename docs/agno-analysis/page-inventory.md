# Agno OS Reference Inventory

Source: Chrome/CDP read-only analysis of `https://os.agno.com` on 2026-06-19.

## Reference Screenshots

All screenshots were captured from the public Demo OS surface at a 1512 x 828 viewport.

| Page | URL | Screenshot |
|---|---|---|
| Home | `https://os.agno.com/try-demo` | `docs/agno-analysis/reference-screenshots/home.png` |
| Chat | `https://os.agno.com/try-demo/chat?type=agent` | `docs/agno-analysis/reference-screenshots/chat.png` |
| Chat deep link | `https://os.agno.com/chat?type=team&id=router-team&session=1534cf8b-ec92-40e3-91ed-2fb1e942267c` | `docs/agno-analysis/next-reference-screenshots/chat-deeplink-reference.png` |
| Chat tool call collapsed | `https://os.agno.com/try-demo/chat?type=agent&id=sage&session={uuid}` | `docs/agno-analysis/next-reference-screenshots/chat-tool-call-collapsed-reference.png` |
| Chat tool call expanded | `https://os.agno.com/try-demo/chat?type=agent&id=sage&session={uuid}` | `docs/agno-analysis/next-reference-screenshots/chat-tool-call-expanded-reference.png` |
| Sessions | `https://os.agno.com/try-demo/sessions?sort_by=updated_at_desc&type=all&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/sessions.png` |
| Traces | `https://os.agno.com/try-demo/traces?group_by=sessions&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/traces.png` |
| Studio | `https://os.agno.com/try-demo/studio/agents` | `docs/agno-analysis/next-reference-screenshots/studio-list-reference.png` |
| Learning User Memories | `https://os.agno.com/learning/user_memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-user-memory-reference.png` |
| Learning User Profiles | `https://os.agno.com/learning/user_profile?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-user-profile-reference.png` |
| Learning Entity Memories | `https://os.agno.com/learning/entity_memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-entity-memory-reference.png` |
| Learning Session Context | `https://os.agno.com/learning/session_context?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-session-context-reference.png` |
| Learning Decision Logs | `https://os.agno.com/learning/decision_log?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/next-reference-screenshots/learning-decision-log-reference.png` |
| Memory | `https://os.agno.com/try-demo/memory?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/memory.png` |
| Knowledge | `https://os.agno.com/try-demo/knowledge?sort_by=updated_at_desc&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/knowledge.png` |
| Metrics | `https://os.agno.com/try-demo/metrics` | `docs/agno-analysis/reference-screenshots/metrics.png` |
| Approvals | `https://os.agno.com/try-demo/approvals?status=all&page=1&limit=25` | `docs/agno-analysis/reference-screenshots/approvals.png` |
| Scheduler | `https://os.agno.com/try-demo/scheduler` | `docs/agno-analysis/reference-screenshots/scheduler.png` |
| Settings OS interactions | `https://os.agno.com/settings/os` | `docs/agno-analysis/next-reference-screenshots/settings-os-interactions-reference.png` |

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
- The main header breadcrumb shows the active section.
- `User Memories` can render an empty/loading workspace with a centered
  three-dot indicator while the memory page is loading.
- `User Profiles`, `Entity Memories`, `Session Context`, and `Decision Logs`
  reuse a MemoryPage-style entity table under the authenticated shell. Observed
  columns are checkbox, `ENTITY NAME`, `ENTITY TYPE`, and `UPDATED AT`.
- Captured entity rows include `Acme Corp`, `Sarah Chen`, `Project Phoenix`,
  `Q3 Roadmap`, `Stripe`, `Marcus Lee`, `Design System`, `Series A Round`,
  `Kubernetes Migration`, and `Postgres Cluster`.
- Authenticated Learning traffic loads `MemoryPage` assets, performs OS/user/org
  API lookups through `https://os-api.agno.com`, then checks
  `http://localhost:7777/health`.
- When the connected AgentOS is down, Learning keeps the table visible behind a
  blurred inactive overlay with `AgentOS not active`, `LEARN MORE`, `REFRESH`,
  `EXPLORE A LIVE DEMO AGENTOS`, and a bottom-right
  `Failed to connect to the AgentOS` toast.
- Local implementation now adds `/learning/[section]`, sidebar subnav, shell
  active-state support for every Learning child route, User Memories loading
  state, and inactive entity-table states for the other four sections.

### Chat

- Main modes: agent/team/workflow selection inferred from `type` query param.
- Authenticated deep links preserve `type`, `id`, and `session` query params to
  restore the selected runnable entity and conversation state.
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
  - The authenticated route
    `/chat?type=team&id=router-team&session=1534cf8b-ec92-40e3-91ed-2fb1e942267c`
    restores the Router Team context, a user message `write insights on ai
    trends in 200 words`, a `Finance Agent: Working...` step accordion, and an
    assistant answer beginning `Artificial Intelligence (AI) continues to be a
    transformative force in 2024`.
  - When the connected local AgentOS is unreachable, the authenticated route
    checks `http://localhost:7777/health` and overlays `AgentOS not active`,
    `Your AgentOS is connected but is not active. After running the AgentOS you
    need to refresh the page.`, `LEARN MORE`, `REFRESH`, `EXPLORE A LIVE DEMO
    AGENTOS`, and `Failed to connect to the AgentOS`.
  - Authenticated shell/API traffic observed for the deep link includes
    `POST https://os-api.agno.com/api/v1/auth/authenticate`, organization/user
    lookups, `GET /api/v1/operating-systems/`, operating-system security keys,
    and billing lookup before local AgentOS health checks.
  - Local implementation now initializes `/chat` from `type/id/session`, syncs
    later entity/session changes back into the URL, restores the captured Router
    Team conversation, and renders the inactive-AgentOS overlay for the captured
    session.
  - Sending a runnable Demo OS agent prompt from
    `/try-demo/chat?type=agent&id=sage` first checks
    `GET https://demo-os-production-823a.up.railway.app/health`, then posts
    `multipart/form-data` to
    `POST https://demo-os-production-823a.up.railway.app/agents/sage/runs`.
    Observed form fields: `message`, `stream=true`, `session_id`, and `user_id`.
    The run response is `text/event-stream`.
  - After the streamed run completes, the route mutates to
    `/try-demo/chat?type=agent&id=sage&session={uuid}` and fetches
    `/sessions/{session}?type=agent&user_id={user}&db_id=demo-os-db` plus
    `/sessions/{session}/runs?session_id={session}&type=agent&db_id=demo-os-db&table=agno_sessions`.
  - Completed chat UI adds the first user prompt as a breadcrumb segment,
    renders the user message with a compact `NN` avatar, renders an assistant
    run row such as `Worked for 2 s`, keeps the composer placeholder as `Ask
    anything...`, and shows copy/metrics actions below the assistant answer.
  - Opening `SESSIONS` after a completed run shrinks the chat canvas and renders
    a right inspector around 500px wide with title `Sessions`, a close icon, the
    active prompt title as a highlighted row, and previous session titles below
    it.
  - Local implementation now mirrors this completed-run structure for preview
    and backend chat responses: textarea composer, Enter-to-send, URL session
    sync, first-prompt breadcrumb, run duration row, copy/metrics actions, and a
    completed-session inspector list.
  - When a completed run includes a tool call, Agno renders a compact uppercase
    pill such as `1 TOOL CALLED` above the assistant run row. The pill includes a
    tool icon and chevron and opens a right-side inspector when clicked.
  - The Tool Calls inspector uses the same around-500px right panel geometry as
    other Chat inspectors, with title `Tool Calls`, an `x` close control, and a
    bordered accordion row such as `SEARCH_AGNO`.
  - Local implementation now mirrors the observed tool-call run state for Agno
    prompts: `1 TOOL CALLED` appears in the conversation and opens a `Tool
    Calls` inspector containing `SEARCH_AGNO`.

### Sessions

- Header context: `Database demo-os-db` and `Table agno_sessions`.
- Controls: `View: All` dropdown and `Updated at` column sort state. No export
  control is visible on the Agno Sessions reference screen.
- View menu options: All, Agents, Teams, Workflows. Selecting Teams updates the
  URL to `type=team` and issues `GET /sessions?page=1&type=team&limit=25&sort_by=updated_at&sort_order=desc&db_id=demo-os-db&table=agno_sessions`.
- Initial API request: `GET https://demo-os-production-823a.up.railway.app/sessions?page=1&limit=25&sort_by=updated_at&sort_order=desc&db_id=demo-os-db&table=agno_sessions`.
- Table columns: checkbox, Session Name, Updated At.
- Pagination footer: previous button, page input, `/ 3`, next button.
- Row text click did not navigate or open a details panel during CDP testing;
  row selection is represented by the checkbox column.
- Local parity iteration on 2026-06-19 replaced the generic DataTable with a
  dedicated Sessions table: Agno-style View radio menu, URL query sync,
  25-row pagination, row checkboxes, and filter-specific data subsets.

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

- Header: `Approvals` with a `View: All` status filter.
- Status menu: grouped popover with header `Status` and radio options All,
  Pending, Approved, Rejected.
- Content: vertical approval rows rather than a database table. Each row shows
  tool/action name on the left, target agent/team/workflow and date on the
  right, parameters below, and Deny/Approve controls only for pending items.
- Observed sample rows include `web_search`, `execute_sql`, `send_email`,
  `deploy_service`, `process_payment`, `publish_article`, `scale_cluster`,
  `create_user_account`, `revoke_access`, and `send_campaign`.
- Non-destructive filter interaction: selecting Pending updates the URL to
  `/try-demo/approvals?status=pending&page=1&limit=25`; no approvals-specific
  business API request was observed during public Demo OS filtering.
- Demo state overlays `Admin access required` messaging over a blurred approval
  list: `Approval can only be viewed and managed by admins. Demo OS users don't
  have access.`
- Local implementation follows the vertical approval list, status radio menu,
  URL query sync, pending-only Deny/Approve controls, local-safe decision state,
  and the blurred admin-access overlay.

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
  - In OS & Security, `ADD TAG` and custom-header add controls are disabled
    until their inputs are populated. The lower section includes a custom
    headers helper line, a dedicated `Danger zone`, a red `DELETE AGENTOS`
    command, and a bottom `SAVE` command that stays disabled until edits.
  - Local implementation now mirrors the OS & Security interaction states:
    copy feedback for AgentOS ID, security-key generation placeholder, tag
    addition, custom header add/remove rows, enabled save state after edits, and
    the separated danger-zone block.
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

- Whether local AgentOS routes provide enough data for traces, memories, knowledge, metrics, evals, approvals, and scheduler, or whether MX-specific facade endpoints are needed.
- Pixel-diff tolerance and viewport matrix for final 1:1 screenshot verification.
