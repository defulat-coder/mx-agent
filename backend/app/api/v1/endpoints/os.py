"""MX AgentOS console facade endpoints."""

from fastapi import APIRouter

from app.schemas.os import (
    OSEntitiesResponse,
    OSMetricsResponse,
    OSOverviewResponse,
    OSSettingsResponse,
    OSTableResponse,
)
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
