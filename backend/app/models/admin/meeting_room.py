"""会议室模型"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MeetingRoom(Base):
    """会议室信息。

    Attributes:
        name: 会议室名称
        floor: 楼层
        capacity: 容纳人数
        equipment: 设备描述
        status: 状态（available/maintenance）
    """

    __tablename__ = "meeting_rooms"

    name: Mapped[str] = mapped_column(String(64), comment="会议室名称")
    floor: Mapped[str] = mapped_column(String(16), comment="楼层")
    capacity: Mapped[int] = mapped_column(Integer, comment="容纳人数")
    equipment: Mapped[str] = mapped_column(String(256), default="", comment="设备（投影/白板/视频等）")
    status: Mapped[str] = mapped_column(String(16), default="available", comment="状态")
