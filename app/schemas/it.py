"""IT 运维相关响应 Schema — 工单、设备资产的 Pydantic 模型"""

import datetime as dt

from pydantic import BaseModel, Field


# ── 设备资产 Schema ──────────────────────────────────────────


class ITAssetResponse(BaseModel):
    """设备资产信息"""

    asset_id: int = Field(description="设备 ID")
    asset_no: str = Field(description="资产编号")
    type: str = Field(description="设备类型")
    brand: str = Field(description="品牌")
    model_name: str = Field(description="型号")
    status: str = Field(description="资产状态")
    employee_id: int | None = Field(default=None, description="当前使用人 ID")
    employee_name: str | None = Field(default=None, description="当前使用人姓名")
    purchase_date: dt.date | None = Field(default=None, description="采购日期")
    warranty_expire: dt.date | None = Field(default=None, description="保修到期日")


# ── 工单 Schema ──────────────────────────────────────────────


class ITTicketResponse(BaseModel):
    """工单信息"""

    ticket_id: int = Field(description="工单 ID")
    ticket_no: str = Field(description="工单编号")
    type: str = Field(description="工单类型")
    title: str = Field(description="工单标题")
    description: str = Field(default="", description="问题描述")
    status: str = Field(description="工单状态")
    priority: str = Field(description="优先级")
    submitter_id: int = Field(description="提交人 ID")
    submitter_name: str = Field(default="", description="提交人姓名")
    handler_id: int | None = Field(default=None, description="处理人 ID")
    handler_name: str | None = Field(default=None, description="处理人姓名")
    resolution: str = Field(default="", description="处理结果")
    resolved_at: dt.datetime | None = Field(default=None, description="解决时间")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


# ── 统计 Schema ──────────────────────────────────────────────


class ITTicketStatsResponse(BaseModel):
    """工单统计"""

    total: int = Field(description="工单总数")
    by_status: dict[str, int] = Field(description="各状态工单数量")
    by_type: dict[str, int] = Field(description="各类型工单数量")
    by_priority: dict[str, int] = Field(description="各优先级工单数量")
    avg_resolve_hours: float | None = Field(default=None, description="平均处理时长（小时）")


class ITAssetStatsResponse(BaseModel):
    """设备统计"""

    total: int = Field(description="设备总数")
    by_status: dict[str, int] = Field(description="各状态设备数量")
    by_type: dict[str, int] = Field(description="各类型设备数量")
    by_department: list[dict] = Field(description="各部门设备分配数量")


class FaultTrendItem(BaseModel):
    """单月故障趋势"""

    month: str = Field(description="月份（YYYY-MM）")
    by_type: dict[str, int] = Field(description="各类型工单数量")
    total: int = Field(description="当月工单总数")


class ITFaultTrendResponse(BaseModel):
    """故障趋势分析"""

    trends: list[FaultTrendItem] = Field(description="月度趋势")
    top_departments: list[dict] = Field(description="高频故障部门 TOP5")
