"""加班记录模型"""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OvertimeRecord(Base):
    """加班申请与记录。

    Attributes:
        employee_id: 员工 ID
        date: 加班日期
        start_time: 开始时间
        end_time: 结束时间
        hours: 加班时长
        type: 工作日/周末/节假日
        status: 待审批/已通过
    """

    __tablename__ = "overtime_records"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    date: Mapped[date] = mapped_column(Date, index=True, comment="加班日期")
    start_time: Mapped[time] = mapped_column(Time, comment="开始时间")
    end_time: Mapped[time] = mapped_column(Time, comment="结束时间")
    hours: Mapped[Decimal] = mapped_column(Numeric(5, 1), comment="加班时长")
    type: Mapped[str] = mapped_column(String(16), default="工作日", comment="加班类型")
    status: Mapped[str] = mapped_column(String(16), default="待审批", comment="审批状态")
