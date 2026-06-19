"""考勤记录模型"""

from datetime import date, time

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AttendanceRecord(Base):
    """每日考勤打卡数据。

    Attributes:
        employee_id: 员工 ID
        date: 日期
        check_in: 上班打卡时间
        check_out: 下班打卡时间
        status: 正常/迟到/早退/缺卡/外勤
        remark: 备注
    """

    __tablename__ = "attendance_records"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    date: Mapped[date] = mapped_column(Date, index=True, comment="考勤日期")
    check_in: Mapped[time | None] = mapped_column(Time, comment="上班打卡时间")
    check_out: Mapped[time | None] = mapped_column(Time, comment="下班打卡时间")
    status: Mapped[str] = mapped_column(String(16), default="正常", comment="考勤状态")
    remark: Mapped[str] = mapped_column(String(256), default="", comment="备注")
