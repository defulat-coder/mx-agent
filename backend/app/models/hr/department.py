"""部门模型"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Department(Base):
    """部门信息，支持树形层级结构。

    Attributes:
        name: 部门名称
        parent_id: 上级部门 ID
        manager_id: 部门负责人 ID
    """

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(64), comment="部门名称")
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), comment="上级部门ID")
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), comment="部门负责人ID")
