"""创建所有数据库表 — 基于 SQLAlchemy metadata.create_all"""

import asyncio

from app.core.database import engine
from app.models.base import Base
from app.models.hr import *  # noqa: F401, F403  # 确保所有模型注册到 Base.metadata


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("所有表创建完成")


if __name__ == "__main__":
    asyncio.run(main())
