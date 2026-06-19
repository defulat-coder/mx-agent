"""IT 设备流转记录模型"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ITAssetHistory(Base):
    """IT 设备分配/回收/调拨历史记录。

    Attributes:
        asset_id: 设备 ID
        action: 操作类型（assign/reclaim/transfer）
        from_employee_id: 原使用人 ID
        to_employee_id: 新使用人 ID
        operated_by: 操作人 ID
        remark: 备注
    """

    __tablename__ = "it_asset_history"

    asset_id: Mapped[int] = mapped_column(ForeignKey("it_assets.id"), comment="设备ID")
    action: Mapped[str] = mapped_column(String(16), comment="操作类型")
    from_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), comment="原使用人ID")
    to_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), comment="新使用人ID")
    operated_by: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="操作人ID")
    remark: Mapped[str] = mapped_column(String(256), default="", comment="备注")
