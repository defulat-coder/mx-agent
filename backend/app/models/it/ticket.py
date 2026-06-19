"""IT 工单模型"""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ITTicket(Base):
    """IT 服务工单。

    Attributes:
        ticket_no: 工单编号，全局唯一（格式 IT-T-xxxx）
        type: 工单类型（repair/password_reset/software_install/permission/other）
        title: 工单标题
        description: 问题描述
        status: 工单状态（open/in_progress/resolved/closed）
        priority: 优先级（low/medium/high/urgent）
        submitter_id: 提交人 ID
        handler_id: 处理人 ID
        resolution: 处理结果
        resolved_at: 解决时间
    """

    __tablename__ = "it_tickets"

    ticket_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="工单编号")
    type: Mapped[str] = mapped_column(String(32), comment="工单类型")
    title: Mapped[str] = mapped_column(String(256), comment="工单标题")
    description: Mapped[str] = mapped_column(Text, default="", comment="问题描述")
    status: Mapped[str] = mapped_column(String(16), default="open", comment="工单状态")
    priority: Mapped[str] = mapped_column(String(16), default="medium", comment="优先级")
    submitter_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), comment="提交人ID")
    handler_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), comment="处理人ID")
    resolution: Mapped[str] = mapped_column(Text, default="", comment="处理结果")
    resolved_at: Mapped[datetime | None] = mapped_column(comment="解决时间")
