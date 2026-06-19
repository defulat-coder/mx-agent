"""个人发展计划 (IDP) 模型"""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DevelopmentPlan(Base):
    """员工个人发展计划，跟踪发展目标和完成进度。

    Attributes:
        employee_id: 员工 ID
        plan_year: 计划年度
        goal: 发展目标描述
        category: 目标分类（技术深耕/管理转型/跨领域拓展/专业认证）
        actions: 具体行动计划
        status: 进行中/已完成/已放弃
        progress: 完成进度 0-100
        deadline: 目标截止日期
    """

    __tablename__ = "development_plans"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    plan_year: Mapped[int] = mapped_column(comment="计划年度")
    goal: Mapped[str] = mapped_column(String(256), comment="发展目标")
    category: Mapped[str] = mapped_column(String(32), comment="目标分类")
    actions: Mapped[str] = mapped_column(String(512), comment="行动计划")
    status: Mapped[str] = mapped_column(String(16), comment="状态")
    progress: Mapped[int] = mapped_column(default=0, comment="完成进度百分比")
    deadline: Mapped[date] = mapped_column(comment="截止日期")
