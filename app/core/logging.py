"""日志配置 — 初始化 loguru，拦截 stdlib logging 到 loguru，日志自动携带 request_id。"""

import logging
import sys

from loguru import logger

from app.config import settings
from app.core.context import get_request_id


class InterceptHandler(logging.Handler):
    """拦截 stdlib logging，转发到 loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        """将 stdlib LogRecord 转发到 loguru，保持调用栈深度正确。"""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _patcher(record: dict) -> None:  # type: ignore[type-arg]  # loguru record 类型为 dict
    """向日志记录注入 request_id。"""
    record["extra"]["request_id"] = get_request_id()


def setup_logging() -> None:
    """初始化 loguru 日志系统。"""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{extra[request_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    logger.configure(patcher=_patcher)

    # 控制台输出
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=log_format,
    )

    # 文件输出（可选）
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            level=settings.LOG_LEVEL,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            encoding="utf-8",
            format=log_format,
        )

    # 拦截 stdlib logging（uvicorn, sqlalchemy 等）
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).handlers = [InterceptHandler()]
