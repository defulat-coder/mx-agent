"""SQLAlchemy 声明式基类 — 提供 id、created_at、updated_at 公共字段"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), comment="更新时间")
