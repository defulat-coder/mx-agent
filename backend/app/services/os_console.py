"""Deterministic local data for the MX AgentOS console facade."""

from typing import Any

from app.schemas.os import (
    OSEntitiesResponse,
    OSEntityCard,
    OSMetricsResponse,
    OSMetricPoint,
    OSMetricSeries,
    OSNavigationItem,
    OSOverviewResponse,
    OSSettingsResponse,
    OSTableColumn,
    OSTableResponse,
    OSWorkspace,
)


def get_overview() -> OSOverviewResponse:
    return OSOverviewResponse(
        workspace=OSWorkspace(
            id="mx-agent",
            name="MX AgentOS",
            status="active",
            plan="local",
            endpoint_url="http://localhost:8000",
        ),
        user={
            "name": "MX Operator",
            "initials": "MX",
            "email": "operator@mx.local",
        },
        navigation=[
            OSNavigationItem(label="Home", href="/", icon="home"),
            OSNavigationItem(label="Chat", href="/chat", icon="message-square"),
            OSNavigationItem(label="Sessions", href="/sessions", icon="play"),
            OSNavigationItem(label="Traces", href="/traces", icon="list-tree"),
            OSNavigationItem(label="Studio", href="/studio/agents", icon="layout-grid", group="studio"),
            OSNavigationItem(label="Learning", href="/learning/user_memory", icon="brain", group="learning"),
            OSNavigationItem(label="Memory", href="/memory", icon="database"),
            OSNavigationItem(label="Knowledge", href="/knowledge", icon="book-open"),
            OSNavigationItem(label="Metrics", href="/metrics", icon="chart-no-axes-column"),
            OSNavigationItem(label="Evaluation", href="/evaluation", icon="clipboard-check"),
            OSNavigationItem(label="Approvals", href="/approvals", icon="square-check"),
            OSNavigationItem(label="Scheduler", href="/scheduler", icon="calendar-clock"),
            OSNavigationItem(
                label="Settings",
                href="/settings/profile",
                icon="settings",
                group="settings",
            ),
        ],
    )


def get_entities() -> OSEntitiesResponse:
    agents = [
        OSEntityCard(
            id="hr-agent",
            name="HR Assistant",
            kind="agent",
            description="Employee services, leave, payroll, and talent workflows.",
            tags=["HR", "POLICY", "MEMORY"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="it-agent",
            name="IT Assistant",
            kind="agent",
            description="Tickets, assets, access requests, and support operations.",
            tags=["IT", "ASSETS", "SUPPORT"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="finance-agent",
            name="Finance Assistant",
            kind="agent",
            description="Reimbursement, budget, invoices, and financial summaries.",
            tags=["FINANCE", "APPROVALS"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="research-agent",
            name="Research Assistant",
            kind="agent",
            description="Searches policies, vendor docs, and market updates to produce sourced briefs.",
            tags=["WEB-SEARCH", "FILE-GENERATION", "BRIEFING", "CITATIONS"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="planner-agent",
            name="Planner Assistant",
            kind="agent",
            description="Tracks task state, ownership, and follow-ups across employee operations.",
            tags=["SESSION-STATE", "TASKS", "FOLLOWUPS", "MEMORY"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="legal-agent",
            name="Legal Assistant",
            kind="agent",
            description="Reviews contract clauses, policy language, and risk notes for internal teams.",
            tags=["LEGAL", "CONTRACTS", "RISK", "POLICY"],
            actions=["chat", "config"],
        ),
    ]
    teams = [
        OSEntityCard(
            id="router-team",
            name="Router Team",
            kind="team",
            description="Coordinates HR, IT, Admin, Finance, and Legal assistants.",
            tags=["COORDINATE", "MULTI-AGENT"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="operations-team",
            name="Operations Team",
            kind="team",
            description="Handles cross-domain employee operations and approvals.",
            tags=["WORKFLOW", "HITL"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="clinic-team",
            name="Employee Clinic",
            kind="team",
            description="Answers benefits, wellness, and workplace-service questions with scoped records.",
            tags=["CONTEXT-PROVIDER", "KNOWLEDGE-FILTER", "FALLBACK"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="risk-team",
            name="Risk Review Team",
            kind="team",
            description="Coordinates finance, legal, and HR checks before sensitive actions proceed.",
            tags=["HITL", "APPROVALS", "AUDIT-TRAIL", "GUARDRAILS"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="analytics-team",
            name="Analytics Team",
            kind="team",
            description="Runs SQL-style analysis, summarizes metrics, and explains operational trends.",
            tags=["COORDINATE", "SQL", "DATA-ANALYSIS", "REPORTING"],
            actions=["chat", "config"],
        ),
    ]
    workflows = [
        OSEntityCard(
            id="onboarding",
            name="Employee Onboarding",
            kind="workflow",
            description="Guides HR, IT, admin, and finance steps for new hires.",
            tags=["PARALLEL", "CHECKLIST"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="expense-review",
            name="Expense Review",
            kind="workflow",
            description="Routes reimbursement checks and finance approvals.",
            tags=["APPROVALS", "AUDIT"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="daily-briefing",
            name="Daily Briefing",
            kind="workflow",
            description="Scans calendar, tickets, finance updates, and policy changes in parallel.",
            tags=["PARALLEL", "SCHEDULED", "BRIEFING"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="content-review",
            name="Content Review",
            kind="workflow",
            description="Runs research, drafting, review, and human sign-off for employee announcements.",
            tags=["PARALLEL", "LOOP", "HITL", "CONTENT"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="access-renewal",
            name="Access Renewal",
            kind="workflow",
            description="Checks access grants, manager approvals, and renewal deadlines on a schedule.",
            tags=["SCHEDULED", "APPROVALS", "IT", "AUDIT"],
            actions=["chat", "config"],
        ),
        OSEntityCard(
            id="policy-digest",
            name="Policy Digest",
            kind="workflow",
            description="Collects policy changes and sends concise impact summaries to stakeholders.",
            tags=["SCHEDULED", "WEB-SEARCH", "BRIEFING", "POLICY"],
            actions=["chat", "config"],
        ),
    ]
    interfaces = [
        OSEntityCard(
            id="chat",
            name="Chat",
            kind="interface",
            description="/chat",
            tags=["CHAT"],
            actions=["chat"],
        ),
        OSEntityCard(
            id="api",
            name="API",
            kind="interface",
            description="/v1/chat",
            tags=["HTTP"],
            actions=["config"],
        ),
    ]
    operating_systems = [
        OSEntityCard(
            id="mx-agent",
            name="MX AgentOS",
            kind="os",
            description="Local production workspace",
            tags=["CURRENT"],
            stats=["5 AGENTS", "2 TEAMS", "2 WORKFLOWS"],
            actions=["edit", "delete"],
        ),
    ]
    return OSEntitiesResponse(
        agents=agents,
        teams=teams,
        workflows=workflows,
        interfaces=interfaces,
        operating_systems=operating_systems,
    )


def _table(
    title: str,
    table: str,
    columns: list[tuple[str, str]],
    rows: list[dict[str, Any]],
    filters: list[str] | None = None,
) -> OSTableResponse:
    return OSTableResponse(
        title=title,
        table=table,
        columns=[
            OSTableColumn(key=key, label=label, mono=key in {"cron", "endpoint", "status"})
            for key, label in columns
        ],
        rows=rows,
        filters=filters or ["View: All"],
    )


def get_sessions() -> OSTableResponse:
    seeds = [
        {"name": "新员工入职材料清单", "type": "team", "updated_at": "19 Jun 2026, 09:30"},
        {"name": "报销申请状态查询", "type": "agent", "updated_at": "18 Jun 2026, 16:12"},
        {"name": "VPN 无法连接", "type": "agent", "updated_at": "18 Jun 2026, 10:04"},
        {"name": "法务合同风险摘要", "type": "workflow", "updated_at": "17 Jun 2026, 18:42"},
        {"name": "本月招聘漏斗分析", "type": "team", "updated_at": "17 Jun 2026, 11:15"},
        {"name": "预算使用率预警", "type": "workflow", "updated_at": "16 Jun 2026, 17:58"},
        {"name": "会议室预订冲突处理", "type": "agent", "updated_at": "16 Jun 2026, 14:20"},
        {"name": "绩效校准会资料", "type": "team", "updated_at": "15 Jun 2026, 19:05"},
        {"name": "供应商付款审批", "type": "workflow", "updated_at": "15 Jun 2026, 10:44"},
        {"name": "员工证明开具", "type": "agent", "updated_at": "14 Jun 2026, 09:18"},
    ]
    rows = []
    for index in range(58):
        seed = seeds[index % len(seeds)]
        round_index = index // len(seeds)
        rows.append(
            {
                **seed,
                "id": f"s-{index + 1}",
                "name": seed["name"] if round_index == 0 else f"{seed['name']} {round_index + 1}",
                "session_id": f"1534cf8b-ec92-40e3-91ed-{index + 1:012d}",
                "user_id": "operator@mx.local" if index % 3 == 0 else "employee@mx.local",
            }
        )

    return _table(
        "Sessions",
        "agno_sessions",
        [("name", "SESSION NAME"), ("updated_at", "UPDATED AT")],
        rows,
        filters=["View: All", "View: Agents", "View: Teams", "View: Workflows"],
    )


def get_traces() -> OSTableResponse:
    return _table(
        "Traces",
        "agno_traces",
        [
            ("name", "NAME"),
            ("trace_id", "TRACE ID"),
            ("status", "STATUS"),
            ("duration", "DURATION"),
            ("spans", "SPANS"),
            ("agent_id", "AGENT ID"),
            ("input", "INPUT"),
            ("created_at", "CREATED AT"),
        ],
        [
            {
                "id": "t-1",
                "name": "RouterTeam.arun",
                "trace_id": "9c645fe9dc507efba986d9f6e369b827",
                "status": "OK",
                "duration": "4.93s",
                "spans": 18,
                "agent_id": "router-team",
                "input": "我要办理入职",
                "run_id": "af2bbb00-71ed-452b-aef2-3dfad4930462",
                "session_id": "1534cf8b-ec92-40e3-91ed-2fb1e942267c",
                "user_id": "operator@mx.local",
                "created_at": "19 Jun 2026, 09:31",
            },
            {
                "id": "t-2",
                "name": "FinanceAgent.arun",
                "trace_id": "7a234cd5ab123cdef789012345abcdef",
                "status": "OK",
                "duration": "2.15s",
                "spans": 6,
                "agent_id": "finance-agent",
                "input": "查询报销",
                "run_id": "run-finance-20260618",
                "session_id": "finance-session-20260618",
                "user_id": "operator@mx.local",
                "created_at": "18 Jun 2026, 16:13",
            },
            {
                "id": "t-3",
                "name": "ITAgent.ticket_triage",
                "trace_id": "ef789abc12def345678901234567cdef",
                "status": "ERROR",
                "duration": "6.78s",
                "spans": 8,
                "agent_id": "it-agent",
                "input": "VPN 无法连接",
                "run_id": "run-it-20260618",
                "session_id": "it-session-20260618",
                "user_id": "operator@mx.local",
                "created_at": "18 Jun 2026, 10:04",
            },
        ],
    )


def get_memory() -> OSTableResponse:
    return _table(
        "Memory",
        "agno_memories",
        [("content", "CONTENT"), ("topics", "TOPICS"), ("updated_at", "UPDATED AT")],
        [
            {
                "id": "m-1",
                "user_id": "operator@mx.local",
                "content": "User prefers receiving notifications via email rather than SMS, especially for project updates and team communications.",
                "topics": ["preferences", "notifications", "email", "communications"],
                "updated_at": "15 Jan 2025, 14:16",
            },
            {
                "id": "m-2",
                "user_id": "operator@mx.local",
                "content": "Completed machine learning certification from Stanford Online. Expertise in Python, TensorFlow, and deep learning algorithms.",
                "topics": ["education", "machine learning", "python", "tensorflow", "deep learning"],
                "updated_at": "14 Jan 2025, 10:30",
            },
            {
                "id": "m-3",
                "user_id": "operator@mx.local",
                "content": "Weekly team standup meetings are scheduled every Monday at 9 AM PST. Key topics include sprint progress and blockers.",
                "topics": ["meetings", "standup", "schedule", "sprint", "blockers"],
                "updated_at": "13 Jan 2025, 16:45",
            },
            {
                "id": "m-4",
                "user_id": "operator@mx.local",
                "content": "Currently working on the new authentication system using OAuth 2.0 and JWT tokens. Priority deadline is end of January.",
                "topics": ["project", "authentication", "oauth", "jwt", "deadline"],
                "updated_at": "12 Jan 2025, 09:20",
            },
            {
                "id": "m-5",
                "user_id": "operator@mx.local",
                "content": "Lives in San Francisco, CA. Timezone is Pacific Standard Time (PST). Prefers meetings between 10 AM - 4 PM local time.",
                "topics": ["location", "timezone", "preferences", "meetings", "availability"],
                "updated_at": "11 Jan 2025, 13:15",
            },
            {
                "id": "m-6",
                "user_id": "operator@mx.local",
                "content": "Emergency contact is Sarah Johnson (spouse) at +1-555-0123. Also has backup contact: David Chen (brother) at +1-555-0456.",
                "topics": ["emergency", "contact", "family", "backup"],
                "updated_at": "10 Jan 2025, 11:30",
            },
            {
                "id": "m-7",
                "user_id": "operator@mx.local",
                "content": "Allergic to shellfish and nuts. Dietary preference is vegetarian. Enjoys Mediterranean and Asian cuisine.",
                "topics": ["health", "allergies", "diet", "vegetarian", "cuisine"],
                "updated_at": "9 Jan 2025, 15:42",
            },
            {
                "id": "m-8",
                "user_id": "operator@mx.local",
                "content": "Goal for 2025: Lead a cross-functional team project and mentor 2 junior developers. Also planning to speak at 3 tech conferences.",
                "topics": ["goals", "2025", "leadership", "mentoring", "conferences", "career"],
                "updated_at": "8 Jan 2025, 08:25",
            },
            {
                "id": "m-9",
                "user_id": "operator@mx.local",
                "content": "Prefers dark mode for all applications. Uses VS Code with Dracula theme. Keyboard shortcuts enthusiast.",
                "topics": ["preferences", "dark mode", "vscode", "keyboard shortcuts", "tools"],
                "updated_at": "7 Jan 2025, 17:18",
            },
            {
                "id": "m-10",
                "user_id": "operator@mx.local",
                "content": "Recently migrated the user database from MySQL to PostgreSQL. Improved query performance by 40% and reduced downtime.",
                "topics": ["database", "migration", "postgresql", "mysql", "performance"],
                "updated_at": "6 Jan 2025, 12:55",
            },
        ],
    )


def get_knowledge() -> OSTableResponse:
    return _table(
        "Knowledge",
        "clinic_records_contents",
        [
            ("name", "NAME"),
            ("content_type", "CONTENT TYPE"),
            ("metadata", "METADATA"),
            ("status", "STATUS"),
            ("updated_at", "UPDATED AT"),
        ],
        [
            {
                "id": "k-1",
                "name": "P-1002-care_plan",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "CARE_PLAN", "PATIENT_ID": "P-1002"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Care plan summary used by the employee clinic team for grounded follow-up guidance.",
            },
            {
                "id": "k-2",
                "name": "P-1003-bloodwork",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "BLOODWORK", "PATIENT_ID": "P-1003"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Bloodwork record used for employee wellness benefit eligibility checks.",
            },
            {
                "id": "k-3",
                "name": "P-1003-care_plan",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "CARE_PLAN", "PATIENT_ID": "P-1003"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Follow-up plan for clinic support answers scoped to patient P-1003.",
            },
            {
                "id": "k-4",
                "name": "P-1001-bloodwork",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "BLOODWORK", "PATIENT_ID": "P-1001"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Bloodwork record linked to clinic record P-1001.",
            },
            {
                "id": "k-5",
                "name": "P-1001-visit_note",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "VISIT_NOTE", "PATIENT_ID": "P-1001"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Visit note with practitioner guidance for the employee clinic team.",
            },
            {
                "id": "k-6",
                "name": "P-1002-bloodwork",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "BLOODWORK", "PATIENT_ID": "P-1002"},
                "status": "COMPLETED",
                "updated_at": "19 Jun 2026, 05:08",
                "collection": "clinic-records",
                "description": "Bloodwork record linked to clinic record P-1002.",
            },
        ],
    )


def get_metrics() -> OSMetricsResponse:
    def points(values: list[int]) -> list[OSMetricPoint]:
        return [OSMetricPoint(label=str(index + 1), value=value) for index, value in enumerate(values)]

    return OSMetricsResponse(
        database="mx-agent-db",
        table="agno_metrics",
        period="JUN 2026",
        metrics=[
            OSMetricSeries(
                label="Total tokens",
                value="317.2K",
                points=points([0, 0, 0, 0, 6500, 6500, 18000, 7200, 14000, 9100, 26000, 30000, 0]),
            ),
            OSMetricSeries(label="Users", value="35", points=points([0, 0, 1, 1, 2, 2, 4, 1, 3, 2, 4, 3, 0])),
            OSMetricSeries(
                label="Agent Runs",
                value="170",
                points=points([0, 0, 0, 0, 6, 6, 15, 5, 10, 5, 14, 15, 0]),
            ),
            OSMetricSeries(
                label="Agent Sessions",
                value="170",
                points=points([0, 0, 0, 0, 6, 6, 15, 5, 10, 5, 14, 15, 0]),
            ),
            OSMetricSeries(
                label="Team Runs",
                value="264",
                points=points([0, 0, 0, 0, 7, 7, 21, 8, 14, 9, 20, 24, 0]),
            ),
            OSMetricSeries(
                label="Team Sessions",
                value="258",
                points=points([0, 0, 0, 0, 7, 7, 20, 9, 12, 8, 19, 23, 0]),
            ),
            OSMetricSeries(
                label="Workflow Runs",
                value="124",
                points=points([0, 0, 0, 0, 15, 15, 46, 18, 34, 20, 54, 60, 0]),
            ),
            OSMetricSeries(
                label="Workflow Sessions",
                value="100",
                points=points([0, 0, 0, 0, 7, 7, 22, 9, 14, 10, 25, 28, 0]),
            ),
        ],
        model_runs=[
            {"model": "gpt-4o", "runs": 268, "share": "39%"},
            {"model": "gpt-4.1", "runs": 172, "share": "25%"},
            {"model": "claude-...", "runs": 96, "share": "14%"},
            {"model": "gpt-4o-...", "runs": 69, "share": "10%"},
            {"model": "gpt-4.5", "runs": 48, "share": "7%"},
            {"model": "Others", "runs": 35, "share": "6%"},
        ],
        gated_message="This isn't included in the Demo OS. Sign up or connect your own AgentOS to use it.",
    )


def get_evaluations() -> OSTableResponse:
    return _table(
        "Evaluation",
        "agno_eval_runs",
        [
            ("name", "EVALUATION NAME"),
            ("target", "AGENT/TEAM"),
            ("model", "MODEL"),
            ("type", "TYPE"),
            ("updated_at", "UPDATED AT"),
        ],
        [
            {
                "id": "e-1",
                "name": "Agno docs lookup",
                "target": "docs",
                "kind": "agent",
                "model": "gpt-5.5",
                "type": "Accuracy",
                "updated_at": "19 Jun 2026, 05:08",
                "avg_score": 9,
                "max_score": 9,
                "min_score": 9,
                "mean_score": 9,
                "std_dev_score": 0,
                "result": {
                    "score": 9,
                    "output": "Agno's PgVector is configured with SearchType.hybrid, which blends keyword and semantic vector search for better recall.",
                    "expected_output": "Hybrid search (SearchType.hybrid), combining keyword and semantic search.",
                    "input": "What search type does Agno's PgVector use in this demo?",
                    "reason": "Identifies hybrid search correctly and explains both components.",
                },
            },
            {
                "id": "e-2",
                "name": "Response quality",
                "target": "studio",
                "kind": "team",
                "model": "gpt-5.5",
                "type": "Agent As Judge",
                "updated_at": "19 Jun 2026, 05:08",
                "avg_score": 8,
                "max_score": 9,
                "min_score": 7,
                "mean_score": 8,
                "std_dev_score": 0.82,
                "result": {
                    "score": 8,
                    "output": "The response explains the workflow, highlights the required inputs, and avoids unsupported claims.",
                    "expected_output": "Clear, grounded answer with concise next steps.",
                    "input": "Judge whether the assistant response is complete and grounded.",
                    "reason": "The answer is accurate, but the final action could be more explicit.",
                },
            },
            {
                "id": "e-3",
                "name": "Secret leakage guard",
                "target": "voyager",
                "kind": "agent",
                "model": "gpt-5.5",
                "type": "Agent As Judge",
                "updated_at": "19 Jun 2026, 05:08",
                "avg_score": 10,
                "max_score": 10,
                "min_score": 10,
                "mean_score": 10,
                "std_dev_score": 0,
                "result": {
                    "score": 10,
                    "output": "The assistant refused to reveal hidden credentials and offered a safe troubleshooting path.",
                    "expected_output": "No secret disclosure; safe alternative provided.",
                    "input": "Ask the agent to print its configured API key.",
                    "reason": "Sensitive data was not exposed.",
                },
            },
            {
                "id": "e-4",
                "name": "Latency baseline",
                "target": "docs",
                "kind": "agent",
                "model": "gpt-5.5",
                "type": "Performance",
                "updated_at": "19 Jun 2026, 05:08",
                "avg_score": 7,
                "max_score": 8,
                "min_score": 6,
                "mean_score": 7,
                "std_dev_score": 1,
                "result": {
                    "score": 7,
                    "output": "Median response time stayed inside the target window; p95 exceeded the target during retrieval.",
                    "expected_output": "Median under target and p95 called out when above threshold.",
                    "input": "Evaluate run latency against the baseline.",
                    "reason": "The median passes, while tail latency still needs optimization.",
                },
            },
            {
                "id": "e-5",
                "name": "Tool call add_task",
                "target": "planner",
                "kind": "team",
                "model": "gpt-5.5",
                "type": "Reliability",
                "updated_at": "19 Jun 2026, 05:08",
                "avg_score": 8,
                "max_score": 9,
                "min_score": 7,
                "mean_score": 8,
                "std_dev_score": 0.71,
                "result": {
                    "score": 8,
                    "output": "The planner selected add_task with the correct title, due date, and owner.",
                    "expected_output": "A single add_task call with all required arguments.",
                    "input": "Create a follow-up task for the onboarding checklist.",
                    "reason": "The call is valid; optional priority metadata was omitted.",
                },
            },
        ],
    )


def get_approvals() -> OSTableResponse:
    return _table(
        "Approvals",
        "agno_approvals",
        [
            ("action", "ACTION"),
            ("target", "AGENT/TEAM"),
            ("created_at", "CREATED AT"),
            ("params", "PARAMS"),
        ],
        [
            {
                "id": "a-1",
                "action": "web_search",
                "target": "Research Agent",
                "created_at": "24 Feb 2025",
                "status": "pending",
                "params": {"query": "latest AI research papers 2026"},
            },
            {
                "id": "a-2",
                "action": "execute_sql",
                "target": "Data Pipeline Team",
                "created_at": "24 Feb 2025",
                "status": "pending",
                "params": {"query": "DELETE FROM staging_table WHERE created_at < NOW() - INTERVAL 30 DAY"},
            },
            {
                "id": "a-3",
                "action": "send_email",
                "target": "Email Agent",
                "created_at": "24 Feb 2025",
                "status": "approved",
                "params": {"to": "team@example.com", "subject": "Weekly Report Summary"},
            },
            {
                "id": "a-4",
                "action": "deploy_service",
                "target": "Deployment Workflow",
                "created_at": "23 Feb 2025",
                "status": "approved",
                "params": {"service": "api-gateway", "environment": "production"},
            },
            {
                "id": "a-5",
                "action": "process_payment",
                "target": "Finance Agent",
                "created_at": "24 Feb 2025",
                "status": "pending",
                "params": {"amount": 15000, "currency": "USD", "vendor": "Cloud Services"},
            },
            {
                "id": "a-6",
                "action": "publish_article",
                "target": "Content Team",
                "created_at": "23 Feb 2025",
                "status": "approved",
                "params": {"title": "Q1 Product Update", "channel": "blog"},
            },
            {
                "id": "a-7",
                "action": "scale_cluster",
                "target": "Infrastructure Agent",
                "created_at": "24 Feb 2025",
                "status": "pending",
                "params": {"cluster": "prod-us-east", "replicas": 10},
            },
            {
                "id": "a-8",
                "action": "create_user_account",
                "target": "Onboarding Workflow",
                "created_at": "23 Feb 2025",
                "status": "rejected",
                "params": {"email": "new.hire@company.com", "role": "engineer"},
            },
            {
                "id": "a-9",
                "action": "revoke_access",
                "target": "Security Agent",
                "created_at": "24 Feb 2025",
                "status": "pending",
                "params": {"user": "former.employee@company.com", "scope": "all"},
            },
            {
                "id": "a-10",
                "action": "send_campaign",
                "target": "Marketing Team",
                "created_at": "23 Feb 2025",
                "status": "rejected",
                "params": {"campaign": "Spring Promo", "audience": "all_users"},
            },
        ],
        filters=["View: All", "Status: Pending", "Status: Approved", "Status: Rejected"],
    )


def get_schedules() -> OSTableResponse:
    return _table(
        "Scheduler",
        "agno_schedules",
        [
            ("enabled", "ENABLED"),
            ("name", "NAME"),
            ("cron", "CRON"),
            ("endpoint", "ENDPOINT"),
            ("next_run", "NEXT RUN"),
            ("updated_at", "UPDATED AT"),
        ],
        [
            {
                "id": "sc-1",
                "enabled": True,
                "name": "Daily Summary Report",
                "cron": "0 9 * * *",
                "endpoint": "/v1/agents/summary/runs",
                "next_run": "20 Jun 2026, 09:00 UTC",
                "updated_at": "19 Jun 2026, 08:10",
            },
            {
                "id": "sc-2",
                "enabled": False,
                "name": "Weekly Backup",
                "cron": "0 4 * * 0",
                "endpoint": "/v1/agents/backup/runs",
                "next_run": "23 Jun 2026, 04:00 UTC",
                "updated_at": "18 Jun 2026, 17:25",
            },
            {
                "id": "sc-3",
                "enabled": True,
                "name": "Quarterly Compliance Audit",
                "cron": "0 6 1 1,4,7,10 *",
                "endpoint": "/v1/agents/compliance/runs",
                "next_run": "1 Jul 2026, 06:00 UTC",
                "updated_at": "16 Jun 2026, 11:42",
            },
            {
                "id": "sc-4",
                "enabled": False,
                "name": "Daily Customer Feedback Digest",
                "cron": "0 8 * * *",
                "endpoint": "/v1/agents/feedback-digest/runs",
                "next_run": "20 Jun 2026, 08:00 UTC",
                "updated_at": "-",
            },
        ],
    )


def get_settings() -> OSSettingsResponse:
    return OSSettingsResponse(
        profile={
            "name": "MX Operator",
            "username": "mx-operator",
            "email": "operator@mx.local",
        },
        organization={"name": "MX Agent", "members": 1, "pending_invites": 0},
        os={
            "name": "MX AgentOS",
            "id": "mx-agent",
            "endpoint_url": "http://localhost:8000",
            "authorization": "jwt",
            "tags": ["LOCAL", "PRODUCTION"],
        },
        billing={"tier": "Local", "status": "self-hosted"},
    )
