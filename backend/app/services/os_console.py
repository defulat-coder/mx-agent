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
            OSNavigationItem(label="Studio", href="/studio", icon="layout-grid", group="studio"),
            OSNavigationItem(label="Learning", href="/learning", icon="brain", group="learning"),
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
) -> OSTableResponse:
    return OSTableResponse(
        title=title,
        table=table,
        columns=[
            OSTableColumn(key=key, label=label, mono=key in {"cron", "endpoint", "status"})
            for key, label in columns
        ],
        rows=rows,
        filters=["View: All"],
    )


def get_sessions() -> OSTableResponse:
    return _table(
        "Sessions",
        "agno_sessions",
        [("name", "SESSION NAME"), ("updated_at", "UPDATED AT")],
        [
            {"id": "s-1", "name": "新员工入职需要哪些步骤？", "updated_at": "19 Jun 2026, 09:30"},
            {"id": "s-2", "name": "报销申请状态查询", "updated_at": "18 Jun 2026, 16:12"},
            {"id": "s-3", "name": "VPN 无法连接", "updated_at": "18 Jun 2026, 10:04"},
        ],
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
                "content": "User prefers email notifications for project updates.",
                "topics": ["PREFERENCES", "EMAIL"],
                "updated_at": "15 Jan 2026, 14:16",
            },
            {
                "id": "m-2",
                "content": "Manager role can approve team leave requests.",
                "topics": ["HR", "APPROVALS"],
                "updated_at": "14 Jan 2026, 10:30",
            },
        ],
    )


def get_knowledge() -> OSTableResponse:
    return _table(
        "Knowledge",
        "agno_knowledge",
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
                "name": "employee-handbook",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "POLICY"},
                "status": "COMPLETED",
                "updated_at": "18 Jun 2026, 09:27",
            },
            {
                "id": "k-2",
                "name": "finance-policy",
                "content_type": "File",
                "metadata": {"DOC_TYPE": "FINANCE"},
                "status": "COMPLETED",
                "updated_at": "18 Jun 2026, 09:20",
            },
        ],
    )


def get_metrics() -> OSMetricsResponse:
    points = [
        OSMetricPoint(label=str(day), value=value)
        for day, value in [(1, 4), (8, 9), (15, 12), (22, 8), (29, 14)]
    ]
    return OSMetricsResponse(
        period="JUN 2026",
        metrics=[
            OSMetricSeries(label="Total tokens", value="317.2K", points=points),
            OSMetricSeries(label="Users", value="35", points=points),
            OSMetricSeries(label="Agent Runs", value="170", points=points),
            OSMetricSeries(label="Team Runs", value="264", points=points),
        ],
        model_runs=[
            {"model": "glm-4-plus", "share": "54%"},
            {"model": "gpt-4o", "share": "26%"},
            {"model": "others", "share": "20%"},
        ],
        gated_message="Detailed cost analytics will be connected in a later phase.",
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
                "name": "router-smoke",
                "target": "router-team",
                "model": "glm-4-plus",
                "type": "acceptance",
                "updated_at": "19 Jun 2026, 08:00",
            }
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
                "action": "approve_leave",
                "target": "HR Assistant",
                "created_at": "19 Jun 2026",
                "params": {"employee": "MX0001", "days": 1},
            }
        ],
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
                "updated_at": "-",
            }
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
