"""数据库连接 — 异步引擎、会话工厂及依赖注入会话。"""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def _enable_sqlite_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
    """为每个 SQLite 连接启用外键约束。"""
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


if settings.DATABASE_URL.startswith("sqlite"):
    event.listen(engine.sync_engine, "connect", _enable_sqlite_foreign_keys)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """应用启动时自动建表，并确保 data 目录存在。"""
    database_url = make_url(settings.DATABASE_URL)
    if database_url.get_backend_name() == "sqlite" and database_url.database not in {None, ":memory:"}:
        Path(database_url.database).parent.mkdir(parents=True, exist_ok=True)

    from app.models.base import Base
    # 确保所有模型已导入，触发表注册
    import app.models.hr  # noqa: F401
    import app.models.it  # noqa: F401
    import app.models.admin  # noqa: F401
    import app.models.finance  # noqa: F401
    import app.models.legal  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供异步数据库会话，请求结束后自动 commit 或 rollback。

    Yields:
        AsyncSession: 可用的事务会话
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
