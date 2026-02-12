"""应用入口 — AgentOS 运行时，集成自定义 middleware、异常处理和业务路由。"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.os.middleware import JWTMiddleware
from fastapi import FastAPI
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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：启动时初始化日志和业务数据库，关闭时释放连接。"""
    setup_logging()
    await init_db()
    yield
    await engine.dispose()


# base_app：保留自定义 middleware、exception handlers、业务路由
base_app = FastAPI(title=settings.APP_NAME)

base_app.add_middleware(RequestLoggingMiddleware)
base_app.add_middleware(RequestIDMiddleware)

base_app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
base_app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

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
    excluded_route_paths=["/docs", "/redoc", "/openapi.json", "/health"],
)

if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=True)
