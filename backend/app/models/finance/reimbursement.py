"""报销单模型"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Reimbursement(Base):
    """报销单。

    Attributes:
        reimbursement_no: 报销单号
        employee_id: 申请人 ID
        type: 报销类型（差旅/餐费/交通/办公/招待/其他）
        amount: 报销金额
        status: 状态（pending/approved/rejected/returned/paid）
        reviewer_id: 审核人 ID
        review_remark: 审核备注
        reviewed_at: 审核时间
        department_id: 部门 ID
    """

    __tablename__ = "reimbursements"

    reimbursement_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="报销单号")
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="申请人ID")
    type: Mapped[str] = mapped_column(String(32), comment="报销类型")
    amount: Mapped[float] = mapped_column(Float, comment="报销金额")
    status: Mapped[str] = mapped_column(String(16), default="pending", comment="状态")
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), default=None, comment="审核人ID")
    review_remark: Mapped[str] = mapped_column(String(256), default="", comment="审核备注")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="审核时间")
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), comment="部门ID")
