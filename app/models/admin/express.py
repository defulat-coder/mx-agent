"""快递收发模型"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Express(Base):
    """快递收发记录。

    Attributes:
        tracking_no: 快递单号
        type: 类型（receive/send）
        employee_id: 员工 ID
        courier: 快递公司
        status: 状态（pending/picked_up/sent）
        received_at: 签收时间
        remark: 备注
    """

    __tablename__ = "expresses"

    tracking_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment="快递单号")
    type: Mapped[str] = mapped_column(String(16), comment="类型")
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="员工ID")
    courier: Mapped[str] = mapped_column(String(32), comment="快递公司")
    status: Mapped[str] = mapped_column(String(16), comment="状态")
    received_at: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="签收时间")
    remark: Mapped[str] = mapped_column(String(256), default="", comment="备注")
