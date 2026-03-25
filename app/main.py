"""应用入口 — AgentOS 运行时，集成自定义 middleware、异常处理和业务路由。"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

# 在导入 Agno 相关模块之前初始化 tracing，确保我们的 TracerProvider 优先
from app.core.tracing import setup_tracing, flush_traces
setup_tracing()

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.os.middleware import JWTMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.agents.router_agent import router_team
from app.config import settings
from app.core.database import engine, init_db
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.api.v1.router import v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：启动时初始化日志、业务数据库和知识库，关闭时释放连接。"""
    setup_logging()
    await init_db()

    from app.knowledge.loader import load_knowledge
    await load_knowledge()

    yield
    flush_traces()  # 确保所有 traces 在关闭前发送
    await engine.dispose()


# base_app：保留自定义 middleware、exception handlers、业务路由
base_app = FastAPI(title=settings.APP_NAME)

base_app.add_middleware(RequestLoggingMiddleware)
base_app.add_middleware(RequestIDMiddleware)

base_app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

base_app.include_router(v1_router, prefix="/v1")

# AgentOS
agent_os = AgentOS(
    name="马喜智能助手",
    teams=[router_team],
    base_app=base_app,
    db=SqliteDb(db_file="data/agent_sessions.db"),
    lifespan=lifespan,
    tracing=True,
)

app = agent_os.get_app()

# JWTMiddleware：认证 + session_state 自动注入
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.AUTH_SECRET],
    algorithm="HS256",
    user_id_claim="employee_id",
    session_state_claims=["employee_id", "roles", "department_id"],
    validate=True,
    excluded_route_paths=[
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/agents",
        "/agents/*",
        "/teams",
        "/teams/*",
        "/workflows",
        "/workflows/*",
        "/sessions",
        "/sessions/*",
        "/memories",
        "/memories/*",
        "/memory_topics",
        "/knowledge/*",
        "/traces",
        "/traces/*",
        "/metrics",
        "/metrics/*",
        "/config",
        "/components",
        "/components/*",
        "/models",
        "/databases/*",
        "/eval-runs",
        "/eval-runs/*",
        "/optimize-memories",
        "/user_memory_stats",
        "/trace_session_stats",
    ],
)


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)

    if origin:
        response.headers["access-control-allow-origin"] = origin
        response.headers["access-control-allow-credentials"] = "true"
        response.headers["access-control-allow-methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        response.headers["access-control-allow-headers"] = "content-type, authorization, x-requested-with, accept, origin"
        response.headers["access-control-max-age"] = "600"

    return response


if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=True)
