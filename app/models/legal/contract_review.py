"""合同审查记录模型"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContractReview(Base):
    """合同审查记录。

    Attributes:
        contract_id: 合同 ID
        reviewer_id: 审查人 ID
        action: 审查动作（approved/returned）
        opinion: 审查意见
    """

    __tablename__ = "contract_reviews"

    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), comment="合同ID")
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="审查人ID")
    action: Mapped[str] = mapped_column(String(16), comment="审查动作")
    opinion: Mapped[str] = mapped_column(Text, default="", comment="审查意见")
