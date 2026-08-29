"""报销明细行模型"""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReimbursementItem(Base):
    """报销明细行。

    Attributes:
        reimbursement_id: 报销单 ID
        description: 费用说明
        amount: 金额
        expense_date: 费用日期
        category: 费用科目
    """

    __tablename__ = "reimbursement_items"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_reimbursement_item_amount_positive"),
    )

    reimbursement_id: Mapped[int] = mapped_column(ForeignKey("reimbursements.id"), comment="报销单ID")
    description: Mapped[str] = mapped_column(String(256), comment="费用说明")
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), comment="金额")
    expense_date: Mapped[date] = mapped_column(Date, comment="费用日期")
    category: Mapped[str] = mapped_column(String(32), comment="费用科目")
