"""IT 设备资产模型"""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ITAsset(Base):
    """IT 设备资产信息。

    Attributes:
        asset_no: 资产编号，全局唯一（格式 IT-A-xxxx）
        type: 设备类型（laptop/desktop/monitor/peripheral/other）
        brand: 品牌
        model_name: 型号
        status: 资产状态（idle/in_use/maintenance/scrapped）
        employee_id: 当前使用人 ID（空闲/报废时为 null）
        purchase_date: 采购日期
        warranty_expire: 保修到期日
    """

    __tablename__ = "it_assets"

    asset_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="资产编号")
    type: Mapped[str] = mapped_column(String(32), comment="设备类型")
    brand: Mapped[str] = mapped_column(String(64), default="", comment="品牌")
    model_name: Mapped[str] = mapped_column(String(128), default="", comment="型号")
    status: Mapped[str] = mapped_column(String(16), default="idle", comment="资产状态")
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), comment="当前使用人ID")
    purchase_date: Mapped[date | None] = mapped_column(comment="采购日期")
    warranty_expire: Mapped[date | None] = mapped_column(comment="保修到期日")
