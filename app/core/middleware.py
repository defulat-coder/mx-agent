"""HTTP 中间件 — 请求日志 & request_id 生成/透传。"""

import time
import uuid

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.context import set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求生成/透传 X-Request-ID，存入 contextvars 并写入响应 header。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """生成或复用 request_id，注入上下文并写入响应 header。"""
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        set_request_id(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """记录每个 HTTP 请求的方法、路径、状态码与耗时。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理请求并记录日志。

        Args:
            request: 当前 HTTP 请求
            call_next: 下一个中间件或路由处理函数

        Returns:
            响应对象
        """
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "{method} {path} {status} {duration}ms",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration_ms,
        )
        return response
