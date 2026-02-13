"""合同记录模型"""

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Contract(Base):
    """合同记录。

    Attributes:
        contract_no: 合同编号（唯一）
        title: 合同标题
        type: 合同类型
        party_a: 甲方
        party_b: 乙方
        amount: 合同金额
        start_date: 生效日期
        end_date: 到期日期
        status: 状态（draft/pending/approved/rejected/returned/expired/terminated）
        content: 合同摘要文本
        key_terms: 关键条款（JSON 字符串）
        submitted_by: 提交人 ID
        department_id: 部门 ID
    """

    __tablename__ = "contracts"

    contract_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="合同编号")
    title: Mapped[str] = mapped_column(String(128), comment="合同标题")
    type: Mapped[str] = mapped_column(String(32), comment="合同类型")
    party_a: Mapped[str] = mapped_column(String(128), default="马喜科技有限公司", comment="甲方")
    party_b: Mapped[str] = mapped_column(String(128), comment="乙方")
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, comment="合同金额")
    start_date: Mapped[date] = mapped_column(Date, comment="生效日期")
    end_date: Mapped[date] = mapped_column(Date, comment="到期日期")
    status: Mapped[str] = mapped_column(String(16), default="draft", comment="状态")
    content: Mapped[str] = mapped_column(Text, default="", comment="合同摘要")
    key_terms: Mapped[str] = mapped_column(Text, default="", comment="关键条款JSON")
    submitted_by: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="提交人ID")
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), comment="部门ID")
