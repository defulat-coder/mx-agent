"""技能标签模型"""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Skill(Base):
    """员工技能标签

    Attributes:
        employee_id: 员工 ID
        name: 技能名称
        category: 技能分类（技术/管理/业务/通用）
        level: 技能等级（初级/中级/高级/专家）
        source: 来源（自评/上级评/认证）
        verified: 是否已确认
    """

    __tablename__ = "skills"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    name: Mapped[str] = mapped_column(String(64), comment="技能名称")
    category: Mapped[str] = mapped_column(String(16), comment="技能分类")
    level: Mapped[str] = mapped_column(String(8), comment="技能等级")
    source: Mapped[str] = mapped_column(String(8), comment="来源")
    verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已确认")
