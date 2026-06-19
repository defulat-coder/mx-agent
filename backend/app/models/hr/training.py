"""培训记录/计划模型"""

from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Training(Base):
    """培训记录与培训计划（合表），通过 status 区分生命周期阶段。

    Attributes:
        employee_id: 员工 ID
        course_name: 课程名称
        category: 分类（专业技能/通用素质/管理能力/合规必修）
        hours: 学时
        score: 考试分数，无考试则为空
        status: 待开始/进行中/已完成/未通过
        provider: 培训机构或内训讲师
        assigned_by: 指派人，空字符串表示自主报名
        deadline: 截止日期
        completed_date: 完成日期
    """

    __tablename__ = "trainings"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    course_name: Mapped[str] = mapped_column(String(128), comment="课程名称")
    category: Mapped[str] = mapped_column(String(32), comment="培训分类")
    hours: Mapped[Decimal] = mapped_column(comment="学时")
    score: Mapped[int | None] = mapped_column(comment="考试分数")
    status: Mapped[str] = mapped_column(String(16), comment="状态")
    provider: Mapped[str] = mapped_column(String(64), comment="培训机构/讲师")
    assigned_by: Mapped[str] = mapped_column(String(64), default="", comment="指派人")
    deadline: Mapped[date | None] = mapped_column(comment="截止日期")
    completed_date: Mapped[date | None] = mapped_column(comment="完成日期")
