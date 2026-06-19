"""v1 路由聚合 — 注册并挂载各业务端点的 router。"""

from fastapi import APIRouter

from app.api.v1.endpoints.evals import router as evals_router

v1_router = APIRouter()
v1_router.include_router(evals_router)
