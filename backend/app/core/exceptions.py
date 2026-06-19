"""应用异常及统一处理 — 自定义异常类与 FastAPI 异常处理器。"""

import traceback
from datetime import datetime, timezone

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.core.context import get_request_id
from app.core.error_codes import ErrorCode


class AppException(Exception):
    """应用自定义异常基类，携带业务错误码、HTTP 状态码与错误描述。

    Attributes:
        code: 业务错误码
        message: 用户可读的错误描述
        status_code: HTTP 状态码
        detail: 可选的补充信息
    """

    def __init__(
        self,
        code: int = ErrorCode.BAD_REQUEST,
        message: str = "请求错误",
        status_code: int = 400,
        detail: str | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail


class UnauthorizedException(AppException):
    """401 未认证异常，用于 token 缺失、过期或无效。"""

    def __init__(self, code: int = ErrorCode.TOKEN_MISSING, message: str = "未认证"):
        super().__init__(code=code, message=message, status_code=401)


class ForbiddenException(AppException):
    """403 权限不足异常。"""

    def __init__(self, code: int = ErrorCode.FORBIDDEN, message: str = "无权访问"):
        super().__init__(code=code, message=message, status_code=403)


class NotFoundException(AppException):
    """404 资源未找到异常。"""

    def __init__(self, code: int = ErrorCode.NOT_FOUND, message: str = "资源不存在"):
        super().__init__(code=code, message=message, status_code=404)


class ValidationException(AppException):
    """422 参数校验异常。"""

    def __init__(self, code: int = ErrorCode.VALIDATION_ERROR, message: str = "参数校验失败"):
        super().__init__(code=code, message=message, status_code=422)


class BusinessException(AppException):
    """400 业务逻辑异常。"""

    def __init__(self, code: int = ErrorCode.BAD_REQUEST, message: str = "业务处理失败"):
        super().__init__(code=code, message=message, status_code=400)


class ExternalServiceException(AppException):
    """502 外部服务调用异常。"""

    def __init__(self, code: int = ErrorCode.EXTERNAL_SERVICE_ERROR, message: str = "外部服务调用失败"):
        super().__init__(code=code, message=message, status_code=502)


def _build_error_response(status_code: int, code: int, message: str, detail: str | list | None = None) -> JSONResponse:
    """构建统一格式的错误 JSON 响应。"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "detail": detail,
            "request_id": get_request_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """将 AppException 及其子类转为统一格式 JSON 响应。"""
    return _build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理 Pydantic RequestValidationError，返回字段级错误信息。"""
    errors = [
        {"loc": list(err["loc"]), "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    return _build_error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR,
        message="请求参数校验失败",
        detail=errors,
    )


_HTTP_CODE_MAP: dict[int, int] = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.TOKEN_MISSING,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    422: ErrorCode.VALIDATION_ERROR,
    500: ErrorCode.INTERNAL_ERROR,
}


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 StarletteHTTPException，映射到对应业务错误码。"""
    code = _HTTP_CODE_MAP.get(exc.status_code, exc.status_code * 100 + 1)
    return _build_error_response(
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail) if exc.detail else "请求错误",
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """捕获未处理异常，记录日志并返回 500 通用错误。DEBUG 模式附带 traceback。"""
    logger.exception("Unhandled exception: {}", exc)
    detail = traceback.format_exc() if settings.DEBUG else None
    return _build_error_response(
        status_code=500,
        code=ErrorCode.INTERNAL_ERROR,
        message="服务内部错误",
        detail=detail,
    )
