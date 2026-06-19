"""项目经历模型"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProjectExperience(Base):
    """员工项目参与记录

    Attributes:
        employee_id: 员工 ID
        project_name: 项目名称
        role: 角色（负责人/核心成员/参与者）
        start_date: 开始日期
        end_date: 结束日期，为空表示进行中
        description: 项目描述
        achievement: 关键成果
    """

    __tablename__ = "project_experiences"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    project_name: Mapped[str] = mapped_column(String(128), comment="项目名称")
    role: Mapped[str] = mapped_column(String(16), comment="角色")
    start_date: Mapped[date] = mapped_column(Date, comment="开始日期")
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None, comment="结束日期")
    description: Mapped[str] = mapped_column(String(512), default="", comment="项目描述")
    achievement: Mapped[str] = mapped_column(String(512), default="", comment="关键成果")
