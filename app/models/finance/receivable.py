"""应收款模型"""

from datetime import date

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Receivable(Base):
    """应收款。

    Attributes:
        receivable_no: 应收单号
        customer: 客户
        amount: 金额
        due_date: 到期日
        status: 状态（pending/received/overdue）
        description: 说明
    """

    __tablename__ = "receivables"

    receivable_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="应收单号")
    customer: Mapped[str] = mapped_column(String(128), comment="客户")
    amount: Mapped[float] = mapped_column(Float, comment="金额")
    due_date: Mapped[date] = mapped_column(Date, comment="到期日")
    status: Mapped[str] = mapped_column(String(16), comment="状态")
    description: Mapped[str] = mapped_column(String(256), default="", comment="说明")
