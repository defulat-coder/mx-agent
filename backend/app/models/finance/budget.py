"""部门预算模型"""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Budget(Base):
    """部门年度预算。

    Attributes:
        department_id: 部门 ID
        year: 年度
        total_amount: 预算总额
        used_amount: 已使用金额
        status: 状态（active/frozen）
    """

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("department_id", "year", name="uq_budget_department_year"),
        CheckConstraint(
            "total_amount >= 0 AND used_amount >= 0 AND used_amount <= total_amount",
            name="ck_budget_amounts_valid",
        ),
    )

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), comment="部门ID")
    year: Mapped[int] = mapped_column(Integer, comment="年度")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), comment="预算总额")
    used_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, comment="已使用金额")
    status: Mapped[str] = mapped_column(String(16), default="active", comment="状态")
