"""请求上下文 — 基于 contextvars 存储 request_id，贯穿请求生命周期。"""

from contextvars import ContextVar

_request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """获取当前请求的 request_id。"""
    return _request_id_var.get()


def set_request_id(request_id: str) -> None:
    """设置当前请求的 request_id。"""
    _request_id_var.set(request_id)
