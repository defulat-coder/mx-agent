"""办公用品申领单模型"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SupplyRequest(Base):
    """办公用品申领单。

    Attributes:
        employee_id: 申请人 ID
        items: 申领物品（JSON 格式）
        status: 状态（pending/approved/rejected）
        approved_by: 审批人 ID
        remark: 备注
    """

    __tablename__ = "supply_requests"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="申请人ID")
    items: Mapped[str] = mapped_column(Text, default="", comment="申领物品（JSON格式）")
    status: Mapped[str] = mapped_column(String(16), default="pending", comment="状态")
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), default=None, comment="审批人ID")
    remark: Mapped[str] = mapped_column(String(256), default="", comment="备注")
