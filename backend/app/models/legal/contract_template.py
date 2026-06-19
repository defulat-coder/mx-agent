"""合同模板模型"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContractTemplate(Base):
    """合同模板。

    Attributes:
        name: 模板名称
        type: 合同类型（劳动合同/保密协议/采购合同/销售合同/服务合同/其他）
        description: 模板说明
        file_url: OA 下载链接
    """

    __tablename__ = "contract_templates"

    name: Mapped[str] = mapped_column(String(64), comment="模板名称")
    type: Mapped[str] = mapped_column(String(32), comment="合同类型")
    description: Mapped[str] = mapped_column(Text, default="", comment="模板说明")
    file_url: Mapped[str] = mapped_column(String(256), default="", comment="下载链接")
