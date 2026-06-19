"""会议室预订模型"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RoomBooking(Base):
    """会议室预订记录。

    Attributes:
        room_id: 会议室 ID
        employee_id: 预订人 ID
        title: 会议主题
        start_time: 开始时间（30 分钟对齐）
        end_time: 结束时间（30 分钟对齐）
        status: 状态（active/cancelled/completed）
    """

    __tablename__ = "room_bookings"

    room_id: Mapped[int] = mapped_column(ForeignKey("meeting_rooms.id"), comment="会议室ID")
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="预订人ID")
    title: Mapped[str] = mapped_column(String(128), comment="会议主题")
    start_time: Mapped[datetime] = mapped_column(DateTime, comment="开始时间")
    end_time: Mapped[datetime] = mapped_column(DateTime, comment="结束时间")
    status: Mapped[str] = mapped_column(String(16), default="active", comment="状态")
