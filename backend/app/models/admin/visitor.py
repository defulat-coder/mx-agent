"""访客预约模型"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Visitor(Base):
    """访客预约记录。

    Attributes:
        visitor_name: 访客姓名
        company: 来访单位
        phone: 联系电话
        host_id: 接待人 ID
        visit_date: 来访日期
        visit_time: 来访时间段
        purpose: 来访目的
        status: 状态（pending/checked_in/checked_out/cancelled）
    """

    __tablename__ = "visitors"

    visitor_name: Mapped[str] = mapped_column(String(64), comment="访客姓名")
    company: Mapped[str] = mapped_column(String(128), default="", comment="来访单位")
    phone: Mapped[str] = mapped_column(String(32), default="", comment="联系电话")
    host_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="接待人ID")
    visit_date: Mapped[date] = mapped_column(Date, comment="来访日期")
    visit_time: Mapped[str] = mapped_column(String(16), default="", comment="来访时间段")
    purpose: Mapped[str] = mapped_column(String(256), default="", comment="来访目的")
    status: Mapped[str] = mapped_column(String(16), default="pending", comment="状态")
