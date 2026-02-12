"""假期余额与请假记录模型"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LeaveBalance(Base):
    """员工各类假期余额。

    Attributes:
        employee_id: 员工 ID
        year: 年度
        leave_type: 年假/调休/病假/事假/婚假/产假等
        total_days: 总天数
        used_days: 已用天数
        remaining_days: 剩余天数
    """

    __tablename__ = "leave_balances"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    year: Mapped[int] = mapped_column(comment="年度")
    leave_type: Mapped[str] = mapped_column(String(16), comment="假期类型")
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0, comment="总天数")
    used_days: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0, comment="已用天数")
    remaining_days: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0, comment="剩余天数")


class LeaveRequest(Base):
    """请假申请记录。

    Attributes:
        employee_id: 员工 ID
        leave_type: 假期类型
        start_date: 开始日期
        end_date: 结束日期
        days: 请假天数
        reason: 请假原因
        status: 待审批/已通过/已拒绝/已撤销
    """

    __tablename__ = "leave_requests"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    leave_type: Mapped[str] = mapped_column(String(16), comment="假期类型")
    start_date: Mapped[date] = mapped_column(Date, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, comment="结束日期")
    days: Mapped[Decimal] = mapped_column(Numeric(5, 1), comment="请假天数")
    reason: Mapped[str] = mapped_column(String(256), default="", comment="请假原因")
    status: Mapped[str] = mapped_column(String(16), default="待审批", comment="审批状态")
