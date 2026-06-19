"""预算使用记录模型"""

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BudgetUsage(Base):
    """预算使用记录。

    Attributes:
        budget_id: 预算 ID
        reimbursement_id: 关联报销单 ID
        amount: 使用金额
        category: 费用科目
        description: 说明
        used_date: 使用日期
    """

    __tablename__ = "budget_usages"

    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"), comment="预算ID")
    reimbursement_id: Mapped[int | None] = mapped_column(ForeignKey("reimbursements.id"), default=None, comment="关联报销单ID")
    amount: Mapped[float] = mapped_column(Float, comment="使用金额")
    category: Mapped[str] = mapped_column(String(32), comment="费用科目")
    description: Mapped[str] = mapped_column(String(256), default="", comment="说明")
    used_date: Mapped[date] = mapped_column(Date, comment="使用日期")
