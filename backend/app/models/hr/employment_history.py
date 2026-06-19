"""在职履历模型"""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EmploymentHistory(Base):
    """员工在职期间岗位变动记录。

    Attributes:
        employee_id: 员工 ID
        start_date: 起始日期
        end_date: 结束日期，为空表示当前岗位
        department: 部门名称
        position: 岗位
        level: 职级
        change_type: 变动类型（入职/转正/晋升/调岗/降级）
        remark: 备注
    """

    __tablename__ = "employment_histories"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    start_date: Mapped[date] = mapped_column(comment="起始日期")
    end_date: Mapped[date | None] = mapped_column(comment="结束日期")
    department: Mapped[str] = mapped_column(String(64), comment="部门名称")
    position: Mapped[str] = mapped_column(String(64), comment="岗位")
    level: Mapped[str] = mapped_column(String(32), comment="职级")
    change_type: Mapped[str] = mapped_column(String(16), comment="变动类型")
    remark: Mapped[str] = mapped_column(String(256), default="", comment="备注")
