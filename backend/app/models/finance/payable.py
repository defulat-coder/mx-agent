"""应付款模型"""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Payable(Base):
    """应付款。

    Attributes:
        payable_no: 应付单号
        vendor: 供应商
        amount: 金额
        due_date: 到期日
        status: 状态（pending/paid/overdue）
        description: 说明
    """

    __tablename__ = "payables"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payable_amount_positive"),
    )

    payable_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="应付单号")
    vendor: Mapped[str] = mapped_column(String(128), comment="供应商")
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), comment="金额")
    due_date: Mapped[date] = mapped_column(Date, comment="到期日")
    status: Mapped[str] = mapped_column(String(16), comment="状态")
    description: Mapped[str] = mapped_column(String(256), default="", comment="说明")
