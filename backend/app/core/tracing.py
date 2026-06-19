"""Tracing 初始化 — 集成 Langfuse

参考文档: https://langfuse.com/integrations/frameworks/agno-agents
Langfuse SDK 会自动设置全局 OpenTelemetry TracerProvider，
确保在导入 agno 之前初始化 langfuse client 即可。
"""

import os

from app.config import settings
from app.core.logging import logger

_initialized = False
_langfuse_client = None


def setup_tracing() -> None:
    """初始化 Langfuse tracing。

    Langfuse SDK 初始化时会自动设置全局 OpenTelemetry TracerProvider，
    所有通过 OTel 创建的 spans 都会自动发送到 Langfuse。
    如果 Langfuse 配置缺失，记录警告但允许应用继续启动。
    """
    global _initialized, _langfuse_client
    if _initialized:
        return

    # 检查配置是否完整
    if not settings.LANGFUSE_SECRET_KEY or not settings.LANGFUSE_PUBLIC_KEY:
        logger.warning(
            "Langfuse 配置缺失 (LANGFUSE_SECRET_KEY 或 LANGFUSE_PUBLIC_KEY)，"
            "tracing 功能已禁用"
        )
        return

    try:
        # 设置 Langfuse 环境变量（langfuse SDK 会自动读取）
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_BASE_URL"] = settings.LANGFUSE_BASE_URL

        # 导入并初始化 Langfuse client
        # 这会自动设置全局 OpenTelemetry TracerProvider
        from langfuse import get_client

        _langfuse_client = get_client()

        # 验证连接
        if not _langfuse_client.auth_check():
            logger.warning("Langfuse 认证失败，请检查 API keys 和 base URL")
            _langfuse_client = None
            return

        _initialized = True
        logger.info(f"Langfuse tracing 已初始化，数据将发送到 {settings.LANGFUSE_BASE_URL}")

        # 启用 Agno Instrumentor 来追踪 agent 调用
        try:
            from openinference.instrumentation.agno import AgnoInstrumentor

            AgnoInstrumentor().instrument()
            logger.info("Agno Instrumentor 已启用")
        except ImportError:
            logger.warning("openinference-instrumentation-agno 未安装，agent 自动追踪已禁用")

    except ImportError as e:
        logger.warning(f"缺少必要的依赖: {e}，tracing 功能已禁用")
    except Exception as e:
        logger.warning(f"Tracing 初始化失败: {e}，应用将继续运行")


def flush_traces() -> None:
    """刷新所有待发送的 traces。在应用关闭前调用。"""
    global _langfuse_client
    try:
        if _langfuse_client:
            _langfuse_client.flush()
            logger.info("Langfuse traces 已刷新")
    except Exception as e:
        logger.warning(f"刷新 traces 失败: {e}")


def get_langfuse_client():
    """获取 Langfuse client 实例。"""
    return _langfuse_client


def set_user_attributes(employee_id: int | None = None, roles: list[str] | None = None) -> None:
    """将用户身份信息注入当前 span 的属性中。

    Args:
        employee_id: 员工 ID
        roles: 角色列表
    """
    if _langfuse_client is None:
        return

    try:
        from opentelemetry.trace import get_current_span

        current_span = get_current_span()
        if current_span and current_span.is_recording():
            if employee_id is not None:
                current_span.set_attribute("user.id", str(employee_id))
                current_span.set_attribute("employee_id", employee_id)
            if roles:
                current_span.set_attribute("user.roles", ",".join(roles))
    except Exception:
        # 静默处理，不影响业务逻辑
        pass
