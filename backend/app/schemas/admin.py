"""行政管理相关响应 Schema"""

import datetime as dt

from pydantic import BaseModel, Field


class MeetingRoomResponse(BaseModel):
    """会议室信息"""

    room_id: int = Field(description="会议室 ID")
    name: str = Field(description="会议室名称")
    floor: str = Field(description="楼层")
    capacity: int = Field(description="容纳人数")
    equipment: str = Field(default="", description="设备")
    status: str = Field(description="状态")


class RoomBookingResponse(BaseModel):
    """会议室预订信息"""

    booking_id: int = Field(description="预订 ID")
    room_id: int = Field(description="会议室 ID")
    room_name: str = Field(default="", description="会议室名称")
    employee_id: int = Field(description="预订人 ID")
    employee_name: str = Field(default="", description="预订人姓名")
    title: str = Field(description="会议主题")
    start_time: dt.datetime = Field(description="开始时间")
    end_time: dt.datetime = Field(description="结束时间")
    status: str = Field(description="状态")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


class OfficeSupplyResponse(BaseModel):
    """办公用品库存"""

    supply_id: int = Field(description="用品 ID")
    name: str = Field(description="用品名称")
    category: str = Field(description="分类")
    stock: int = Field(description="库存数量")
    unit: str = Field(description="单位")


class SupplyRequestResponse(BaseModel):
    """办公用品申领单"""

    request_id: int = Field(description="申领单 ID")
    employee_id: int = Field(description="申请人 ID")
    employee_name: str = Field(default="", description="申请人姓名")
    items: str = Field(description="申领物品（JSON）")
    status: str = Field(description="状态")
    approved_by: int | None = Field(default=None, description="审批人 ID")
    remark: str = Field(default="", description="备注")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


class ExpressResponse(BaseModel):
    """快递收发信息"""

    express_id: int = Field(description="快递 ID")
    tracking_no: str = Field(description="快递单号")
    type: str = Field(description="类型")
    employee_id: int = Field(description="员工 ID")
    employee_name: str = Field(default="", description="员工姓名")
    courier: str = Field(description="快递公司")
    status: str = Field(description="状态")
    received_at: dt.datetime | None = Field(default=None, description="签收时间")
    remark: str = Field(default="", description="备注")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


class VisitorResponse(BaseModel):
    """访客预约信息"""

    visitor_id: int = Field(description="访客记录 ID")
    visitor_name: str = Field(description="访客姓名")
    company: str = Field(default="", description="来访单位")
    phone: str = Field(default="", description="联系电话")
    host_id: int = Field(description="接待人 ID")
    host_name: str = Field(default="", description="接待人姓名")
    visit_date: dt.date = Field(description="来访日期")
    visit_time: str = Field(default="", description="来访时间段")
    purpose: str = Field(default="", description="来访目的")
    status: str = Field(description="状态")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


class RoomUsageStatsResponse(BaseModel):
    """会议室使用统计"""

    total_rooms: int = Field(description="会议室总数")
    total_bookings: int = Field(description="预订总数")
    by_room: list[dict] = Field(description="各会议室预订数量")


class SupplyStatsResponse(BaseModel):
    """办公用品统计"""

    total_requests: int = Field(description="申领单总数")
    by_status: dict[str, int] = Field(description="各状态数量")
    top_items: list[dict] = Field(description="消耗 TOP5")
