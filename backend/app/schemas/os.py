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
