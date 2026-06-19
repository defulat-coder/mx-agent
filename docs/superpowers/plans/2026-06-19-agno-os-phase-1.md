# Agno OS Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first production-grade MX AgentOS console slice: Agno-style app shell, core pages, backend `/v1/os/*` facade, live chat integration, and screenshot verification baseline.

**Architecture:** Add a stable backend OS facade that returns local product-shaped data and keeps `POST /v1/chat` as the execution endpoint. Replace the minimal Next.js scaffold with a route-aware operational console composed from small UI primitives and page data adapters. Verify by backend tests, frontend lint/build, and screenshot comparison against `docs/agno-analysis/reference-screenshots`.

**Tech Stack:** FastAPI, Pydantic, pytest, Agno AgentOS, Next.js App Router, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, lucide-react, pnpm.

---

## File Structure

Backend files:

- Create `backend/app/schemas/os.py`: Pydantic response models for overview, entities, tables, metrics, settings, and schedules.
- Create `backend/app/services/os_console.py`: deterministic local data provider and facade helper functions.
- Create `backend/app/api/v1/endpoints/os.py`: `/v1/os/*` FastAPI router.
- Modify `backend/app/api/v1/router.py`: include the OS router.
- Create `backend/tests/test_os_facade.py`: response contract tests for the new facade.

Frontend files:

- Modify `frontend/src/app/layout.tsx`: metadata and root body sizing for console UI.
- Modify `frontend/src/app/globals.css`: Agno-style theme tokens and utility classes.
- Replace `frontend/src/app/page.tsx`: Home page.
- Create `frontend/src/app/chat/page.tsx`, `sessions/page.tsx`, `traces/page.tsx`, `memory/page.tsx`, `knowledge/page.tsx`, `metrics/page.tsx`, `evaluation/page.tsx`, `approvals/page.tsx`, `scheduler/page.tsx`.
- Create `frontend/src/app/settings/profile/page.tsx`, `settings/organization/page.tsx`, `settings/os/page.tsx`, `settings/roles/page.tsx`, `settings/billing/page.tsx`.
- Create `frontend/src/components/agentos/app-shell.tsx`: sidebar, topbar, layout frame.
- Create `frontend/src/components/agentos/command-button.tsx`: compact mono command button.
- Create `frontend/src/components/agentos/entity-card.tsx`: agent/team/workflow/OS cards.
- Create `frontend/src/components/agentos/data-table.tsx`: compact table primitive.
- Create `frontend/src/components/agentos/status-state.tsx`: empty, gated, inactive states.
- Create `frontend/src/components/agentos/chat-surface.tsx`: chat workspace and composer.
- Create `frontend/src/components/agentos/metrics-grid.tsx`: chart-like metric panels.
- Create `frontend/src/lib/agentos-data.ts`: static fallback data and data normalizers.
- Create `frontend/src/lib/agentos-api.ts`: frontend fetch helpers for `/v1/os/*` and `/v1/chat`.
- Create `frontend/src/lib/agentos-types.ts`: shared TypeScript types.

Docs:

- Modify `README.md`: update frontend placeholder drift and add phase-1 run commands.

---

### Task 1: Backend OS Facade Contracts

**Files:**
- Create: `backend/app/schemas/os.py`
- Create: `backend/app/services/os_console.py`
- Create: `backend/tests/test_os_facade.py`

- [ ] **Step 1: Write failing backend contract tests**

Add `backend/tests/test_os_facade.py`:

```python
"""OS console facade contract tests."""

from httpx import AsyncClient


async def test_os_overview_contract(client: AsyncClient):
    resp = await client.get("/v1/os/overview")

    assert resp.status_code == 200
    body = resp.json()
    assert body["workspace"]["name"] == "MX AgentOS"
    assert body["workspace"]["status"] in {"active", "inactive"}
    assert {item["href"] for item in body["navigation"]} >= {
        "/",
        "/chat",
        "/sessions",
        "/traces",
        "/memory",
        "/knowledge",
        "/metrics",
        "/evaluation",
        "/approvals",
        "/scheduler",
    }


async def test_os_entities_contract(client: AsyncClient):
    resp = await client.get("/v1/os/entities")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["agents"]) >= 3
    assert len(body["teams"]) >= 2
    assert len(body["workflows"]) >= 2
    assert body["agents"][0]["actions"] == ["chat", "config"]


async def test_os_sessions_contract(client: AsyncClient):
    resp = await client.get("/v1/os/sessions")

    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Sessions"
    assert [column["key"] for column in body["columns"]] == ["name", "updated_at"]
    assert body["rows"]


async def test_os_metrics_contract(client: AsyncClient):
    resp = await client.get("/v1/os/metrics")

    assert resp.status_code == 200
    body = resp.json()
    assert body["period"] == "JUN 2026"
    assert {metric["label"] for metric in body["metrics"]} >= {"Total tokens", "Users", "Agent Runs"}
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
cd backend
uv run pytest tests/test_os_facade.py -q
```

Expected: fails with `404` or missing `/v1/os/*` routes.

- [ ] **Step 3: Add Pydantic schemas**

Create `backend/app/schemas/os.py` with:

```python
"""Schemas for the MX AgentOS console facade."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class OSWorkspace(BaseModel):
    id: str
    name: str
    status: Literal["active", "inactive"]
    plan: str = "local"
    endpoint_url: str


class OSNavigationItem(BaseModel):
    label: str
    href: str
    icon: str
    group: str = "main"


class OSOverviewResponse(BaseModel):
    workspace: OSWorkspace
    user: dict[str, str]
    navigation: list[OSNavigationItem]


class OSEntityAction(BaseModel):
    kind: Literal["chat", "config", "switch", "edit", "delete"]
    label: str
    href: str


class OSEntityCard(BaseModel):
    id: str
    name: str
    kind: Literal["agent", "team", "workflow", "interface", "os"]
    description: str
    tags: list[str] = Field(default_factory=list)
    stats: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class OSEntitiesResponse(BaseModel):
    agents: list[OSEntityCard]
    teams: list[OSEntityCard]
    workflows: list[OSEntityCard]
    interfaces: list[OSEntityCard]
    operating_systems: list[OSEntityCard]


class OSTableColumn(BaseModel):
    key: str
    label: str
    mono: bool = False


class OSTableResponse(BaseModel):
    title: str
    database: str = "mx-agent-db"
    table: str
    columns: list[OSTableColumn]
    rows: list[dict[str, Any]]
    filters: list[str] = Field(default_factory=list)


class OSMetricPoint(BaseModel):
    label: str
    value: int


class OSMetricSeries(BaseModel):
    label: str
    value: str
    points: list[OSMetricPoint]


class OSMetricsResponse(BaseModel):
    period: str
    metrics: list[OSMetricSeries]
    model_runs: list[dict[str, str | int]]
    gated_message: str | None = None


class OSSettingsResponse(BaseModel):
    profile: dict[str, str]
    organization: dict[str, str | int]
    os: dict[str, Any]
    billing: dict[str, Any]
```

- [ ] **Step 4: Add deterministic facade data service**

Create `backend/app/services/os_console.py` with functions:

```python
"""Deterministic local data for the MX AgentOS console facade."""

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
        user={"name": "MX Operator", "initials": "MX", "email": "operator@mx.local"},
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
            OSNavigationItem(label="Settings", href="/settings/profile", icon="settings", group="settings"),
        ],
    )


def get_entities() -> OSEntitiesResponse:
    agents = [
        OSEntityCard(id="hr-agent", name="HR Assistant", kind="agent", description="Employee services, leave, payroll, and talent workflows.", tags=["HR", "POLICY", "MEMORY"], actions=["chat", "config"]),
        OSEntityCard(id="it-agent", name="IT Assistant", kind="agent", description="Tickets, assets, access requests, and support operations.", tags=["IT", "ASSETS", "SUPPORT"], actions=["chat", "config"]),
        OSEntityCard(id="finance-agent", name="Finance Assistant", kind="agent", description="Reimbursement, budget, invoices, and financial summaries.", tags=["FINANCE", "APPROVALS"], actions=["chat", "config"]),
    ]
    teams = [
        OSEntityCard(id="router-team", name="Router Team", kind="team", description="Coordinates HR, IT, Admin, Finance, and Legal assistants.", tags=["COORDINATE", "MULTI-AGENT"], actions=["chat", "config"]),
        OSEntityCard(id="operations-team", name="Operations Team", kind="team", description="Handles cross-domain employee operations and approvals.", tags=["WORKFLOW", "HITL"], actions=["chat", "config"]),
    ]
    workflows = [
        OSEntityCard(id="onboarding", name="Employee Onboarding", kind="workflow", description="Guides HR, IT, admin, and finance steps for new hires.", tags=["PARALLEL", "CHECKLIST"], actions=["chat", "config"]),
        OSEntityCard(id="expense-review", name="Expense Review", kind="workflow", description="Routes reimbursement checks and finance approvals.", tags=["APPROVALS", "AUDIT"], actions=["chat", "config"]),
    ]
    interfaces = [
        OSEntityCard(id="chat", name="Chat", kind="interface", description="/chat", tags=["CHAT"], actions=["chat"]),
        OSEntityCard(id="api", name="API", kind="interface", description="/v1/chat", tags=["HTTP"], actions=["config"]),
    ]
    operating_systems = [
        OSEntityCard(id="mx-agent", name="MX AgentOS", kind="os", description="Local production workspace", tags=["CURRENT"], stats=["5 AGENTS", "2 TEAMS", "2 WORKFLOWS"], actions=["edit", "delete"]),
    ]
    return OSEntitiesResponse(agents=agents, teams=teams, workflows=workflows, interfaces=interfaces, operating_systems=operating_systems)


def _table(title: str, table: str, columns: list[tuple[str, str]], rows: list[dict]) -> OSTableResponse:
    return OSTableResponse(
        title=title,
        table=table,
        columns=[OSTableColumn(key=key, label=label, mono=key in {"cron", "endpoint", "status"}) for key, label in columns],
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
        [("name", "NAME"), ("status", "STATUS"), ("duration", "DURATION"), ("spans", "SPANS"), ("target", "AGENT/TEAM/WORKFLOW"), ("input", "INPUT"), ("created_at", "CREATED AT")],
        [
            {"id": "t-1", "name": "RouterTeam.arun", "status": "OK", "duration": "4.93s", "spans": 18, "target": "router-team", "input": "我要办理入职", "created_at": "19 Jun 2026, 09:31"},
            {"id": "t-2", "name": "FinanceAgent.arun", "status": "OK", "duration": "2.15s", "spans": 6, "target": "finance-agent", "input": "查询报销", "created_at": "18 Jun 2026, 16:13"},
        ],
    )


def get_memory() -> OSTableResponse:
    return _table(
        "Memory",
        "agno_memories",
        [("content", "CONTENT"), ("topics", "TOPICS"), ("updated_at", "UPDATED AT")],
        [
            {"id": "m-1", "content": "User prefers email notifications for project updates.", "topics": ["PREFERENCES", "EMAIL"], "updated_at": "15 Jan 2026, 14:16"},
            {"id": "m-2", "content": "Manager role can approve team leave requests.", "topics": ["HR", "APPROVALS"], "updated_at": "14 Jan 2026, 10:30"},
        ],
    )


def get_knowledge() -> OSTableResponse:
    return _table(
        "Knowledge",
        "agno_knowledge",
        [("name", "NAME"), ("content_type", "CONTENT TYPE"), ("metadata", "METADATA"), ("status", "STATUS"), ("updated_at", "UPDATED AT")],
        [
            {"id": "k-1", "name": "employee-handbook", "content_type": "File", "metadata": {"DOC_TYPE": "POLICY"}, "status": "COMPLETED", "updated_at": "18 Jun 2026, 09:27"},
            {"id": "k-2", "name": "finance-policy", "content_type": "File", "metadata": {"DOC_TYPE": "FINANCE"}, "status": "COMPLETED", "updated_at": "18 Jun 2026, 09:20"},
        ],
    )


def get_metrics() -> OSMetricsResponse:
    points = [OSMetricPoint(label=str(day), value=value) for day, value in [(1, 4), (8, 9), (15, 12), (22, 8), (29, 14)]]
    return OSMetricsResponse(
        period="JUN 2026",
        metrics=[
            OSMetricSeries(label="Total tokens", value="317.2K", points=points),
            OSMetricSeries(label="Users", value="35", points=points),
            OSMetricSeries(label="Agent Runs", value="170", points=points),
            OSMetricSeries(label="Team Runs", value="264", points=points),
        ],
        model_runs=[{"model": "glm-4-plus", "share": "54%"}, {"model": "gpt-4o", "share": "26%"}, {"model": "others", "share": "20%"}],
        gated_message="Detailed cost analytics will be connected in a later phase.",
    )


def get_evaluations() -> OSTableResponse:
    return _table("Evaluation", "agno_eval_runs", [("name", "EVALUATION NAME"), ("target", "AGENT/TEAM"), ("model", "MODEL"), ("type", "TYPE"), ("updated_at", "UPDATED AT")], [{"id": "e-1", "name": "router-smoke", "target": "router-team", "model": "glm-4-plus", "type": "acceptance", "updated_at": "19 Jun 2026, 08:00"}])


def get_approvals() -> OSTableResponse:
    return _table("Approvals", "agno_approvals", [("action", "ACTION"), ("target", "AGENT/TEAM"), ("created_at", "CREATED AT"), ("params", "PARAMS")], [{"id": "a-1", "action": "approve_leave", "target": "HR Assistant", "created_at": "19 Jun 2026", "params": {"employee": "MX0001", "days": 1}}])


def get_schedules() -> OSTableResponse:
    return _table("Scheduler", "agno_schedules", [("enabled", "ENABLED"), ("name", "NAME"), ("cron", "CRON"), ("endpoint", "ENDPOINT"), ("next_run", "NEXT RUN"), ("updated_at", "UPDATED AT")], [{"id": "sc-1", "enabled": True, "name": "Daily Summary Report", "cron": "0 9 * * *", "endpoint": "/v1/agents/summary/runs", "next_run": "20 Jun 2026, 09:00 UTC", "updated_at": "-"}])


def get_settings() -> OSSettingsResponse:
    return OSSettingsResponse(
        profile={"name": "MX Operator", "username": "mx-operator", "email": "operator@mx.local"},
        organization={"name": "MX Agent", "members": 1, "pending_invites": 0},
        os={"name": "MX AgentOS", "id": "mx-agent", "endpoint_url": "http://localhost:8000", "authorization": "jwt", "tags": ["LOCAL", "PRODUCTION"]},
        billing={"tier": "Local", "status": "self-hosted"},
    )
```

- [ ] **Step 5: Run schema import check**

Run:

```bash
cd backend
uv run python -c "from app.services import os_console; print(os_console.get_overview().workspace.name)"
```

Expected: prints `MX AgentOS`.

---

### Task 2: Backend OS Router

**Files:**
- Create: `backend/app/api/v1/endpoints/os.py`
- Modify: `backend/app/api/v1/router.py`
- Test: `backend/tests/test_os_facade.py`

- [ ] **Step 1: Add router endpoint file**

Create `backend/app/api/v1/endpoints/os.py`:

```python
"""MX AgentOS console facade endpoints."""

from fastapi import APIRouter

from app.schemas.os import OSEntitiesResponse, OSMetricsResponse, OSOverviewResponse, OSSettingsResponse, OSTableResponse
from app.services import os_console

router = APIRouter(prefix="/os", tags=["os-console"])


@router.get("/overview", response_model=OSOverviewResponse)
async def overview() -> OSOverviewResponse:
    return os_console.get_overview()


@router.get("/entities", response_model=OSEntitiesResponse)
async def entities() -> OSEntitiesResponse:
    return os_console.get_entities()


@router.get("/sessions", response_model=OSTableResponse)
async def sessions() -> OSTableResponse:
    return os_console.get_sessions()


@router.get("/traces", response_model=OSTableResponse)
async def traces() -> OSTableResponse:
    return os_console.get_traces()


@router.get("/memory", response_model=OSTableResponse)
async def memory() -> OSTableResponse:
    return os_console.get_memory()


@router.get("/knowledge", response_model=OSTableResponse)
async def knowledge() -> OSTableResponse:
    return os_console.get_knowledge()


@router.get("/metrics", response_model=OSMetricsResponse)
async def metrics() -> OSMetricsResponse:
    return os_console.get_metrics()


@router.get("/evaluations", response_model=OSTableResponse)
async def evaluations() -> OSTableResponse:
    return os_console.get_evaluations()


@router.get("/approvals", response_model=OSTableResponse)
async def approvals() -> OSTableResponse:
    return os_console.get_approvals()


@router.get("/schedules", response_model=OSTableResponse)
async def schedules() -> OSTableResponse:
    return os_console.get_schedules()


@router.get("/settings", response_model=OSSettingsResponse)
async def settings() -> OSSettingsResponse:
    return os_console.get_settings()
```

- [ ] **Step 2: Register router**

Modify `backend/app/api/v1/router.py` to include:

```python
from app.api.v1.endpoints.os import router as os_router
```

and:

```python
v1_router.include_router(os_router)
```

- [ ] **Step 3: Run focused tests**

Run:

```bash
cd backend
uv run pytest tests/test_os_facade.py -q
```

Expected: all tests pass.

- [ ] **Step 4: Run API regression tests**

Run:

```bash
cd backend
uv run pytest tests/test_api.py tests/test_auth.py tests/test_config.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit backend facade**

Run:

```bash
git add backend/app/schemas/os.py backend/app/services/os_console.py backend/app/api/v1/endpoints/os.py backend/app/api/v1/router.py backend/tests/test_os_facade.py
git commit -m "feat: add os console facade"
```

---

### Task 3: Frontend Types, API Client, and Static Fallback Data

**Files:**
- Create: `frontend/src/lib/agentos-types.ts`
- Create: `frontend/src/lib/agentos-api.ts`
- Create: `frontend/src/lib/agentos-data.ts`

- [ ] **Step 1: Add TypeScript types**

Create `frontend/src/lib/agentos-types.ts`:

```ts
export type WorkspaceStatus = "active" | "inactive";

export type NavigationItem = {
  label: string;
  href: string;
  icon: string;
  group: string;
};

export type WorkspaceOverview = {
  workspace: {
    id: string;
    name: string;
    status: WorkspaceStatus;
    plan: string;
    endpoint_url: string;
  };
  user: {
    name: string;
    initials: string;
    email: string;
  };
  navigation: NavigationItem[];
};

export type EntityKind = "agent" | "team" | "workflow" | "interface" | "os";

export type EntityCardData = {
  id: string;
  name: string;
  kind: EntityKind;
  description: string;
  tags: string[];
  stats: string[];
  actions: string[];
};

export type EntitiesResponse = {
  agents: EntityCardData[];
  teams: EntityCardData[];
  workflows: EntityCardData[];
  interfaces: EntityCardData[];
  operating_systems: EntityCardData[];
};

export type TableColumn = {
  key: string;
  label: string;
  mono: boolean;
};

export type TableResponse = {
  title: string;
  database: string;
  table: string;
  columns: TableColumn[];
  rows: Record<string, unknown>[];
  filters: string[];
};

export type MetricsResponse = {
  period: string;
  metrics: Array<{
    label: string;
    value: string;
    points: Array<{ label: string; value: number }>;
  }>;
  model_runs: Array<Record<string, string | number>>;
  gated_message: string | null;
};

export type SettingsResponse = {
  profile: Record<string, string>;
  organization: Record<string, string | number>;
  os: Record<string, unknown>;
  billing: Record<string, unknown>;
};

export type ChatResponse = {
  reply: string;
  action: Record<string, unknown> | null;
  session_id: string | null;
};
```

- [ ] **Step 2: Add API helpers with deterministic fallback**

Create `frontend/src/lib/agentos-api.ts`:

```ts
import type {
  ChatResponse,
  EntitiesResponse,
  MetricsResponse,
  SettingsResponse,
  TableResponse,
  WorkspaceOverview,
} from "@/lib/agentos-types";
import {
  fallbackEntities,
  fallbackMetrics,
  fallbackOverview,
  fallbackSettings,
  fallbackTables,
} from "@/lib/agentos-data";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
      headers: { accept: "application/json" },
    });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function getOverview(): Promise<WorkspaceOverview> {
  return getJson("/v1/os/overview", fallbackOverview);
}

export function getEntities(): Promise<EntitiesResponse> {
  return getJson("/v1/os/entities", fallbackEntities);
}

export function getTable(name: keyof typeof fallbackTables): Promise<TableResponse> {
  return getJson(`/v1/os/${name}`, fallbackTables[name]);
}

export function getMetrics(): Promise<MetricsResponse> {
  return getJson("/v1/os/metrics", fallbackMetrics);
}

export function getSettings(): Promise<SettingsResponse> {
  return getJson("/v1/os/settings", fallbackSettings);
}

export async function sendChatMessage(message: string, sessionId?: string | null): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/v1/chat`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ message, session_id: sessionId ?? undefined }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with HTTP ${response.status}`);
  }

  return (await response.json()) as ChatResponse;
}
```

- [ ] **Step 3: Add fallback data**

Create `frontend/src/lib/agentos-data.ts` by mirroring the backend facade content:

```ts
import type { EntitiesResponse, MetricsResponse, SettingsResponse, TableResponse, WorkspaceOverview } from "@/lib/agentos-types";

export const fallbackOverview: WorkspaceOverview = {
  workspace: {
    id: "mx-agent",
    name: "MX AgentOS",
    status: "active",
    plan: "local",
    endpoint_url: "http://localhost:8000",
  },
  user: {
    name: "MX Operator",
    initials: "MX",
    email: "operator@mx.local",
  },
  navigation: [
    { label: "Home", href: "/", icon: "home", group: "main" },
    { label: "Chat", href: "/chat", icon: "message-square", group: "main" },
    { label: "Sessions", href: "/sessions", icon: "play", group: "main" },
    { label: "Traces", href: "/traces", icon: "list-tree", group: "main" },
    { label: "Studio", href: "/studio", icon: "layout-grid", group: "studio" },
    { label: "Learning", href: "/learning", icon: "brain", group: "learning" },
    { label: "Memory", href: "/memory", icon: "database", group: "main" },
    { label: "Knowledge", href: "/knowledge", icon: "book-open", group: "main" },
    { label: "Metrics", href: "/metrics", icon: "chart-no-axes-column", group: "main" },
    { label: "Evaluation", href: "/evaluation", icon: "clipboard-check", group: "main" },
    { label: "Approvals", href: "/approvals", icon: "square-check", group: "main" },
    { label: "Scheduler", href: "/scheduler", icon: "calendar-clock", group: "main" },
    { label: "Settings", href: "/settings/profile", icon: "settings", group: "settings" },
  ],
};

export const fallbackEntities: EntitiesResponse = {
  agents: [
    { id: "hr-agent", name: "HR Assistant", kind: "agent", description: "Employee services, leave, payroll, and talent workflows.", tags: ["HR", "POLICY", "MEMORY"], stats: [], actions: ["chat", "config"] },
    { id: "it-agent", name: "IT Assistant", kind: "agent", description: "Tickets, assets, access requests, and support operations.", tags: ["IT", "ASSETS", "SUPPORT"], stats: [], actions: ["chat", "config"] },
    { id: "finance-agent", name: "Finance Assistant", kind: "agent", description: "Reimbursement, budget, invoices, and financial summaries.", tags: ["FINANCE", "APPROVALS"], stats: [], actions: ["chat", "config"] },
  ],
  teams: [
    { id: "router-team", name: "Router Team", kind: "team", description: "Coordinates HR, IT, Admin, Finance, and Legal assistants.", tags: ["COORDINATE", "MULTI-AGENT"], stats: [], actions: ["chat", "config"] },
    { id: "operations-team", name: "Operations Team", kind: "team", description: "Handles cross-domain employee operations and approvals.", tags: ["WORKFLOW", "HITL"], stats: [], actions: ["chat", "config"] },
  ],
  workflows: [
    { id: "onboarding", name: "Employee Onboarding", kind: "workflow", description: "Guides HR, IT, admin, and finance steps for new hires.", tags: ["PARALLEL", "CHECKLIST"], stats: [], actions: ["chat", "config"] },
    { id: "expense-review", name: "Expense Review", kind: "workflow", description: "Routes reimbursement checks and finance approvals.", tags: ["APPROVALS", "AUDIT"], stats: [], actions: ["chat", "config"] },
  ],
  interfaces: [
    { id: "chat", name: "Chat", kind: "interface", description: "/chat", tags: ["CHAT"], stats: [], actions: ["chat"] },
    { id: "api", name: "API", kind: "interface", description: "/v1/chat", tags: ["HTTP"], stats: [], actions: ["config"] },
  ],
  operating_systems: [
    { id: "mx-agent", name: "MX AgentOS", kind: "os", description: "Local production workspace", tags: ["CURRENT"], stats: ["5 AGENTS", "2 TEAMS", "2 WORKFLOWS"], actions: ["edit", "delete"] },
  ],
};

const columns = {
  sessions: [{ key: "name", label: "SESSION NAME", mono: false }, { key: "updated_at", label: "UPDATED AT", mono: false }],
  traces: [{ key: "name", label: "NAME", mono: false }, { key: "status", label: "STATUS", mono: true }, { key: "duration", label: "DURATION", mono: false }, { key: "spans", label: "SPANS", mono: false }, { key: "target", label: "AGENT/TEAM/WORKFLOW", mono: false }, { key: "input", label: "INPUT", mono: false }, { key: "created_at", label: "CREATED AT", mono: false }],
  memory: [{ key: "content", label: "CONTENT", mono: false }, { key: "topics", label: "TOPICS", mono: false }, { key: "updated_at", label: "UPDATED AT", mono: false }],
  knowledge: [{ key: "name", label: "NAME", mono: false }, { key: "content_type", label: "CONTENT TYPE", mono: false }, { key: "metadata", label: "METADATA", mono: false }, { key: "status", label: "STATUS", mono: true }, { key: "updated_at", label: "UPDATED AT", mono: false }],
  evaluations: [{ key: "name", label: "EVALUATION NAME", mono: false }, { key: "target", label: "AGENT/TEAM", mono: false }, { key: "model", label: "MODEL", mono: false }, { key: "type", label: "TYPE", mono: false }, { key: "updated_at", label: "UPDATED AT", mono: false }],
  approvals: [{ key: "action", label: "ACTION", mono: false }, { key: "target", label: "AGENT/TEAM", mono: false }, { key: "created_at", label: "CREATED AT", mono: false }, { key: "params", label: "PARAMS", mono: false }],
  schedules: [{ key: "enabled", label: "ENABLED", mono: false }, { key: "name", label: "NAME", mono: false }, { key: "cron", label: "CRON", mono: true }, { key: "endpoint", label: "ENDPOINT", mono: true }, { key: "next_run", label: "NEXT RUN", mono: false }, { key: "updated_at", label: "UPDATED AT", mono: false }],
};

export const fallbackTables: Record<string, TableResponse> = {
  sessions: { title: "Sessions", database: "mx-agent-db", table: "agno_sessions", columns: columns.sessions, rows: [{ id: "s-1", name: "新员工入职需要哪些步骤？", updated_at: "19 Jun 2026, 09:30" }], filters: ["View: All"] },
  traces: { title: "Traces", database: "mx-agent-db", table: "agno_traces", columns: columns.traces, rows: [{ id: "t-1", name: "RouterTeam.arun", status: "OK", duration: "4.93s", spans: 18, target: "router-team", input: "我要办理入职", created_at: "19 Jun 2026, 09:31" }], filters: ["View: All"] },
  memory: { title: "Memory", database: "mx-agent-db", table: "agno_memories", columns: columns.memory, rows: [{ id: "m-1", content: "User prefers email notifications for project updates.", topics: ["PREFERENCES", "EMAIL"], updated_at: "15 Jan 2026, 14:16" }], filters: ["View: All"] },
  knowledge: { title: "Knowledge", database: "mx-agent-db", table: "agno_knowledge", columns: columns.knowledge, rows: [{ id: "k-1", name: "employee-handbook", content_type: "File", metadata: { DOC_TYPE: "POLICY" }, status: "COMPLETED", updated_at: "18 Jun 2026, 09:27" }], filters: ["Clinic Records"] },
  evaluations: { title: "Evaluation", database: "mx-agent-db", table: "agno_eval_runs", columns: columns.evaluations, rows: [{ id: "e-1", name: "router-smoke", target: "router-team", model: "glm-4-plus", type: "acceptance", updated_at: "19 Jun 2026, 08:00" }], filters: ["View: All"] },
  approvals: { title: "Approvals", database: "mx-agent-db", table: "agno_approvals", columns: columns.approvals, rows: [{ id: "a-1", action: "approve_leave", target: "HR Assistant", created_at: "19 Jun 2026", params: { employee: "MX0001", days: 1 } }], filters: ["View: All"] },
  schedules: { title: "Scheduler", database: "mx-agent-db", table: "agno_schedules", columns: columns.schedules, rows: [{ id: "sc-1", enabled: true, name: "Daily Summary Report", cron: "0 9 * * *", endpoint: "/v1/agents/summary/runs", next_run: "20 Jun 2026, 09:00 UTC", updated_at: "-" }], filters: [] },
};

export const fallbackMetrics: MetricsResponse = {
  period: "JUN 2026",
  metrics: [
    { label: "Total tokens", value: "317.2K", points: [{ label: "1", value: 4 }, { label: "8", value: 9 }, { label: "15", value: 12 }, { label: "22", value: 8 }, { label: "29", value: 14 }] },
    { label: "Users", value: "35", points: [{ label: "1", value: 1 }, { label: "8", value: 2 }, { label: "15", value: 3 }, { label: "22", value: 2 }, { label: "29", value: 4 }] },
  ],
  model_runs: [{ model: "glm-4-plus", share: "54%" }, { model: "gpt-4o", share: "26%" }],
  gated_message: "Detailed cost analytics will be connected in a later phase.",
};

export const fallbackSettings: SettingsResponse = {
  profile: { name: "MX Operator", username: "mx-operator", email: "operator@mx.local" },
  organization: { name: "MX Agent", members: 1, pending_invites: 0 },
  os: { name: "MX AgentOS", id: "mx-agent", endpoint_url: "http://localhost:8000", authorization: "jwt", tags: ["LOCAL", "PRODUCTION"] },
  billing: { tier: "Local", status: "self-hosted" },
};
```

- [ ] **Step 4: Run TypeScript check through build**

Run:

```bash
cd frontend
pnpm build
```

Expected: build may still fail because pages/components are not wired yet; TypeScript should not report errors from the three new `agentos-*` lib files. Fix type errors in those files before continuing.

- [ ] **Step 5: Commit frontend data layer**

Run:

```bash
git add frontend/src/lib/agentos-types.ts frontend/src/lib/agentos-api.ts frontend/src/lib/agentos-data.ts
git commit -m "feat: add agentos frontend data layer"
```

---

### Task 4: App Shell and Core UI Primitives

**Files:**
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/app/globals.css`
- Create: `frontend/src/components/agentos/app-shell.tsx`
- Create: `frontend/src/components/agentos/command-button.tsx`
- Create: `frontend/src/components/agentos/entity-card.tsx`
- Create: `frontend/src/components/agentos/status-state.tsx`
- Create: `frontend/src/components/agentos/data-table.tsx`

- [ ] **Step 1: Update root layout metadata and body**

Modify `frontend/src/app/layout.tsx` metadata to:

```ts
export const metadata: Metadata = {
  title: "MX AgentOS",
  description: "MX AgentOS console for enterprise agents",
};
```

Set body class to:

```tsx
<body className="min-h-full bg-[#f6f6f7] text-[#18181b]">{children}</body>
```

- [ ] **Step 2: Extend global CSS**

Add to `frontend/src/app/globals.css` inside `:root`:

```css
  --brand: oklch(0.68 0.22 32);
  --agentos-panel: oklch(1 0 0);
  --agentos-muted-line: oklch(0.91 0 0);
```

Add after base layer:

```css
@layer utilities {
  .font-dmmono {
    font-family: var(--font-geist-mono), "SFMono-Regular", Consolas, monospace;
  }
  .agentos-focus {
    @apply focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-900/30;
  }
}
```

- [ ] **Step 3: Create command button**

Create `frontend/src/components/agentos/command-button.tsx`:

```tsx
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type CommandButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  tone?: "primary" | "secondary" | "outline";
};

export function CommandButton({ children, className, tone = "secondary", ...props }: CommandButtonProps) {
  return (
    <button
      className={cn(
        "agentos-focus inline-flex h-6 shrink-0 items-center justify-center gap-2 rounded-md px-3 font-dmmono text-[12px] font-medium uppercase tracking-normal transition-colors disabled:pointer-events-none disabled:opacity-45",
        tone === "primary" && "bg-zinc-950 text-white hover:bg-zinc-800",
        tone === "secondary" && "bg-zinc-100 text-zinc-950 hover:bg-zinc-200",
        tone === "outline" && "border border-zinc-200 bg-white text-zinc-950 hover:bg-zinc-50",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

- [ ] **Step 4: Create app shell**

Create `frontend/src/components/agentos/app-shell.tsx` with a client component that uses `usePathname`, lucide icons, `fallbackOverview`, and renders the 208px sidebar plus topbar. Include `children` in a white bordered workspace container. Use `CommandButton` for `GET SUPPORT` and `REFRESH`.

Minimum exported signature:

```tsx
"use client";

import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  // render shell around children
}
```

Ensure sidebar labels match the inventory exactly: Home, Chat, Sessions, Traces, Studio, Learning, Memory, Knowledge, Metrics, Evaluation, Approvals, Scheduler, Settings.

- [ ] **Step 5: Create entity card**

Create `frontend/src/components/agentos/entity-card.tsx` that accepts:

```ts
import type { EntityCardData } from "@/lib/agentos-types";

export function EntityCard({ entity }: { entity: EntityCardData }) {
  // render icon, name, description, tags, action buttons
}
```

Actions must render `CHAT` and `CONFIG` command buttons when present.

- [ ] **Step 6: Create data table**

Create `frontend/src/components/agentos/data-table.tsx` with:

```ts
import type { TableResponse } from "@/lib/agentos-types";

export function DataTable({ data }: { data: TableResponse }) {
  // render database/table header, filters, compact table
}
```

Render arrays as chips and objects as `KEY = VALUE` chips.

- [ ] **Step 7: Create status state**

Create `frontend/src/components/agentos/status-state.tsx`:

```tsx
export function StatusState({ title, description, action }: { title: string; description: string; action?: string }) {
  return (
    <div className="mx-auto flex max-w-sm flex-col items-center gap-3 text-center">
      <h3 className="text-[26px] font-medium tracking-normal text-zinc-950">{title}</h3>
      <p className="text-sm leading-6 text-zinc-500">{description}</p>
      {action ? <span className="font-dmmono text-xs uppercase text-zinc-950">{action}</span> : null}
    </div>
  );
}
```

- [ ] **Step 8: Run lint**

Run:

```bash
cd frontend
pnpm lint
```

Expected: no lint errors in new components.

- [ ] **Step 9: Commit shell primitives**

Run:

```bash
git add frontend/src/app/layout.tsx frontend/src/app/globals.css frontend/src/components/agentos
git commit -m "feat: add agentos app shell"
```

---

### Task 5: Home Page

**Files:**
- Replace: `frontend/src/app/page.tsx`

- [ ] **Step 1: Replace Home page**

Replace `frontend/src/app/page.tsx` with a server component that calls `getEntities()` and renders `AppShell`, grouped headings, and `EntityCard` grids:

```tsx
import { AppShell } from "@/components/agentos/app-shell";
import { EntityCard } from "@/components/agentos/entity-card";
import { getEntities } from "@/lib/agentos-api";

export default async function Home() {
  const entities = await getEntities();
  const groups = [
    ["AGENTS", entities.agents],
    ["TEAMS", entities.teams],
    ["WORKFLOWS", entities.workflows],
    ["INTERFACES", entities.interfaces],
    ["ALL OSES", entities.operating_systems],
  ] as const;

  return (
    <AppShell>
      <div className="space-y-8 p-4">
        {groups.map(([title, items]) => (
          <section key={title} className="space-y-3">
            <div className="flex h-8 items-center gap-2 font-dmmono text-xs font-medium uppercase text-zinc-950">
              <span>{title}</span>
            </div>
            <div className="grid gap-4 lg:grid-cols-3">
              {items.map((entity) => (
                <EntityCard key={entity.id} entity={entity} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </AppShell>
  );
}
```

- [ ] **Step 2: Run build**

Run:

```bash
cd frontend
pnpm build
```

Expected: build passes or fails only on routes not yet implemented. Fix Home-specific errors.

- [ ] **Step 3: Commit Home page**

Run:

```bash
git add frontend/src/app/page.tsx
git commit -m "feat: build agentos home page"
```

---

### Task 6: Chat Page

**Files:**
- Create: `frontend/src/components/agentos/chat-surface.tsx`
- Create: `frontend/src/app/chat/page.tsx`

- [ ] **Step 1: Create chat surface client component**

Create `frontend/src/components/agentos/chat-surface.tsx` with a client component that stores `messages`, `input`, `sessionId`, `isSending`, and `error`. On submit, call `sendChatMessage(input, sessionId)`, append user and assistant messages, and update `sessionId`.

Starter prompts:

- `What can MX AgentOS do?`
- `我需要办理入职手续`
- `帮我查询报销申请状态`

- [ ] **Step 2: Create chat route**

Create `frontend/src/app/chat/page.tsx`:

```tsx
import { AppShell } from "@/components/agentos/app-shell";
import { ChatSurface } from "@/components/agentos/chat-surface";

export const metadata = {
  title: "Chat | MX AgentOS",
};

export default function ChatPage() {
  return (
    <AppShell>
      <ChatSurface />
    </AppShell>
  );
}
```

- [ ] **Step 3: Manual chat smoke check**

Run backend and frontend in separate terminals:

```bash
cd backend
uv run python main.py
```

```bash
cd frontend
pnpm dev
```

Open `/chat`, submit `你好`, and verify either a reply appears or a clear auth/backend error appears without losing input.

- [ ] **Step 4: Commit chat page**

Run:

```bash
git add frontend/src/components/agentos/chat-surface.tsx frontend/src/app/chat/page.tsx
git commit -m "feat: build agentos chat page"
```

---

### Task 7: Data Pages and Metrics

**Files:**
- Create data route pages under `frontend/src/app/*/page.tsx`
- Create: `frontend/src/components/agentos/metrics-grid.tsx`

- [ ] **Step 1: Create table-backed pages**

For each route, create the page with `AppShell` and `DataTable`:

- `sessions/page.tsx` uses `getTable("sessions")`
- `traces/page.tsx` uses `getTable("traces")`
- `memory/page.tsx` uses `getTable("memory")`
- `knowledge/page.tsx` uses `getTable("knowledge")`
- `evaluation/page.tsx` uses `getTable("evaluations")`
- `approvals/page.tsx` uses `getTable("approvals")`
- `scheduler/page.tsx` uses `getTable("schedules")`

Example content for `frontend/src/app/sessions/page.tsx`:

```tsx
import { AppShell } from "@/components/agentos/app-shell";
import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function SessionsPage() {
  const data = await getTable("sessions");
  return (
    <AppShell>
      <DataTable data={data} />
    </AppShell>
  );
}
```

- [ ] **Step 2: Create metrics grid**

Create `frontend/src/components/agentos/metrics-grid.tsx` that renders each metric in a bordered panel with title, value, and simple CSS bar chart from points.

- [ ] **Step 3: Create metrics page**

Create `frontend/src/app/metrics/page.tsx`:

```tsx
import { AppShell } from "@/components/agentos/app-shell";
import { MetricsGrid } from "@/components/agentos/metrics-grid";
import { getMetrics } from "@/lib/agentos-api";

export default async function MetricsPage() {
  const data = await getMetrics();
  return (
    <AppShell>
      <MetricsGrid data={data} />
    </AppShell>
  );
}
```

- [ ] **Step 4: Run build**

Run:

```bash
cd frontend
pnpm build
```

Expected: build passes for all page routes created so far.

- [ ] **Step 5: Commit data pages**

Run:

```bash
git add frontend/src/app/sessions frontend/src/app/traces frontend/src/app/memory frontend/src/app/knowledge frontend/src/app/evaluation frontend/src/app/approvals frontend/src/app/scheduler frontend/src/app/metrics frontend/src/components/agentos/metrics-grid.tsx
git commit -m "feat: build agentos data pages"
```

---

### Task 8: Settings Pages and Documentation

**Files:**
- Create settings route pages
- Modify: `README.md`

- [ ] **Step 1: Create settings pages**

Create these pages using `AppShell`, `getSettings()`, and high-fidelity read-only form layouts:

- `frontend/src/app/settings/profile/page.tsx`
- `frontend/src/app/settings/organization/page.tsx`
- `frontend/src/app/settings/os/page.tsx`
- `frontend/src/app/settings/roles/page.tsx`
- `frontend/src/app/settings/billing/page.tsx`

Profile must show `NAME`, `USER NAME`, disabled `EMAIL`, and `SAVE`.

OS & Security must show `AGENTOS NAME`, `AGENTOS ID`, `ENDPOINT URL`, `AUTHORIZATION`, `SECURITY KEY`, `ADDITIONAL SETTINGS`, `CUSTOM HEADERS`, danger zone, and `SAVE`.

- [ ] **Step 2: Update README frontend section**

Modify `README.md` so the project structure describes `frontend/` as a real Next.js application, not a placeholder. Add commands:

```bash
cd frontend
pnpm install
pnpm dev
pnpm build
```

- [ ] **Step 3: Run lint and build**

Run:

```bash
cd frontend
pnpm lint
pnpm build
```

Expected: both pass.

- [ ] **Step 4: Commit settings and docs**

Run:

```bash
git add frontend/src/app/settings README.md
git commit -m "feat: add agentos settings pages"
```

---

### Task 9: Full Verification and Screenshot Pass

**Files:**
- Add local screenshots only if useful under `docs/agno-analysis/local-screenshots/`
- No code changes expected unless verification finds defects.

- [ ] **Step 1: Run backend tests**

Run:

```bash
cd backend
uv run pytest tests/test_os_facade.py tests/test_api.py tests/test_auth.py -q
```

Expected: all pass.

- [ ] **Step 2: Run frontend validation**

Run:

```bash
cd frontend
pnpm lint
pnpm build
```

Expected: both pass.

- [ ] **Step 3: Start local servers**

Run backend:

```bash
cd backend
uv run python main.py
```

Run frontend:

```bash
cd frontend
pnpm dev
```

- [ ] **Step 4: Capture screenshots**

Use Chrome or the in-app browser at 1512 x 828 for:

- `/`
- `/chat`
- `/sessions`
- `/traces`
- `/memory`
- `/knowledge`
- `/metrics`
- `/approvals`
- `/scheduler`

Compare against `docs/agno-analysis/reference-screenshots/*.png` for layout, navigation, spacing, major controls, and text visibility.

- [ ] **Step 5: Mobile smoke pass**

Use a narrow mobile viewport around 390 x 844. Verify:

- Sidebar is usable or collapses.
- Tables do not overlap text.
- Chat composer remains visible and usable.
- Buttons do not truncate labels incoherently.

- [ ] **Step 6: Fix verification defects**

For each defect, change only the relevant file, rerun the narrow validation, and include the fix in the final implementation commit.

- [ ] **Step 7: Final commit**

Run:

```bash
git status --short
git add .
git commit -m "feat: implement agentos phase 1 console"
```

Only commit if `git status --short` shows intended implementation changes.

---

## Self-Review

Spec coverage:

- App shell, Home, Chat, data pages, Metrics, Settings, backend facade, and screenshot verification are each covered by tasks.
- The plan explicitly keeps hosted `os.agno.com` out of runtime dependencies.
- README drift from the spec is handled in Task 8.

Placeholder scan:

- No `TBD`, `TODO`, or "implement later" placeholders are used.
- Phase 1 intentionally labels some actions as unavailable/gated where the approved spec allows read-only or validation-only behavior.

Type consistency:

- Backend route names match frontend fetch helpers, except `evaluation` page maps intentionally to `/v1/os/evaluations` and scheduler maps to `/v1/os/schedules`.
- `TableResponse`, `MetricsResponse`, and `SettingsResponse` names are consistent across backend schemas and frontend types.
