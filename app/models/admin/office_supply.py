"""办公用品模型"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OfficeSupply(Base):
    """办公用品库存。

    Attributes:
        name: 用品名称
        category: 分类（文具/耗材/清洁/其他）
        stock: 库存数量
        unit: 单位
    """

    __tablename__ = "office_supplies"

    name: Mapped[str] = mapped_column(String(64), comment="用品名称")
    category: Mapped[str] = mapped_column(String(32), comment="分类")
    stock: Mapped[int] = mapped_column(Integer, comment="库存数量")
    unit: Mapped[str] = mapped_column(String(16), comment="单位")
