"""HTTP 中间件 — 请求日志 & request_id 生成/透传 & trace_id 注入。"""

import time
import uuid
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

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


class TraceIDMiddleware:
    """纯 ASGI 中间件 — 创建请求级 OTel span 并注入 X-Trace-Id 响应头。

    在请求开始时创建一个父 span，所有 Agent 内部 span 自动成为其子 span，
    共享同一个 trace_id。这样评测系统可以通过 X-Trace-Id 将 score 关联到 Langfuse trace。
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            from opentelemetry import trace as otel_trace

            tracer = otel_trace.get_tracer("mx-agent.http")
        except ImportError:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")

        with tracer.start_as_current_span(f"{method} {path}") as span:
            ctx = span.get_span_context()
            trace_id_hex = ""
            if ctx and ctx.trace_id != otel_trace.INVALID_TRACE_ID:
                trace_id_hex = otel_trace.format_trace_id(ctx.trace_id)

            async def send_wrapper(message: Message) -> None:
                if message["type"] == "http.response.start" and trace_id_hex:
                    headers: list[tuple[bytes, bytes]] = list(message.get("headers", []))
                    headers.append((b"x-trace-id", trace_id_hex.encode()))
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, send_wrapper)
