"""v1 路由聚合 — 注册并挂载各业务端点的 router。"""

from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.evals import router as evals_router
from app.api.v1.endpoints.os import router as os_router

v1_router = APIRouter()
v1_router.include_router(chat_router)
v1_router.include_router(evals_router)
v1_router.include_router(os_router)
