# admin-data-models

行政数据模型 — 6 张 SQLAlchemy ORM 表 + Pydantic Schema

## Requirements

### REQ-ADM-MODEL-1: MeetingRoom 模型

文件 `app/models/admin/meeting_room.py`，表名 `meeting_rooms`。

字段：
- `name`: String(64), comment="会议室名称"
- `floor`: String(16), comment="楼层"
- `capacity`: Integer, comment="容纳人数"
- `equipment`: String(256), default="", comment="设备（投影/白板/视频等）"
- `status`: String(16), default="available", comment="状态"

### REQ-ADM-MODEL-2: RoomBooking 模型

文件 `app/models/admin/room_booking.py`，表名 `room_bookings`。

字段：
- `room_id`: FK → meeting_rooms.id, comment="会议室 ID"
- `employee_id`: FK → employees.id, comment="预订人 ID"
- `title`: String(128), comment="会议主题"
- `start_time`: DateTime, comment="开始时间"
- `end_time`: DateTime, comment="结束时间"
- `status`: String(16), default="active", comment="状态"

### REQ-ADM-MODEL-3: OfficeSupply 模型

文件 `app/models/admin/office_supply.py`，表名 `office_supplies`。

字段：
- `name`: String(64), comment="用品名称"
- `category`: String(32), comment="分类"
- `stock`: Integer, comment="库存数量"
- `unit`: String(16), comment="单位"

### REQ-ADM-MODEL-4: SupplyRequest 模型

文件 `app/models/admin/supply_request.py`，表名 `supply_requests`。

字段：
- `employee_id`: FK → employees.id, comment="申请人 ID"
- `items`: Text, comment="申领物品（JSON 格式）"
- `status`: String(16), default="pending", comment="状态"
- `approved_by`: FK → employees.id, nullable, comment="审批人 ID"
- `remark`: String(256), default="", comment="备注"

### REQ-ADM-MODEL-5: Express 模型

文件 `app/models/admin/express.py`，表名 `expresses`。

字段：
- `tracking_no`: String(64), unique, index, comment="快递单号"
- `type`: String(16), comment="类型"（receive/send）
- `employee_id`: FK → employees.id, comment="员工 ID"
- `courier`: String(32), comment="快递公司"
- `status`: String(16), comment="状态"
- `received_at`: DateTime, nullable, comment="签收时间"
- `remark`: String(256), default="", comment="备注"

### REQ-ADM-MODEL-6: Visitor 模型

文件 `app/models/admin/visitor.py`，表名 `visitors`。

字段：
- `visitor_name`: String(64), comment="访客姓名"
- `company`: String(128), default="", comment="来访单位"
- `phone`: String(32), default="", comment="联系电话"
- `host_id`: FK → employees.id, comment="接待人 ID"
- `visit_date`: Date, comment="来访日期"
- `visit_time`: String(16), default="", comment="来访时间段"
- `purpose`: String(256), default="", comment="来访目的"
- `status`: String(16), default="pending", comment="状态"

### REQ-ADM-MODEL-7: __init__.py 导出

`app/models/admin/__init__.py` 导入并导出全部 6 个模型。

### REQ-ADM-MODEL-8: Pydantic Schema

`app/schemas/admin.py` 定义：
- MeetingRoomResponse
- RoomBookingResponse
- OfficeSupplyResponse
- SupplyRequestResponse
- ExpressResponse
- VisitorResponse
- RoomUsageStatsResponse
- SupplyStatsResponse

所有字段带 `Field(description="中文说明")`。

## Scenarios

- 所有模型继承 Base（含 id / created_at / updated_at）
- 外键关联 employees.id
- meeting_rooms 与 room_bookings 1:N
- start_time / end_time 需 30 分钟对齐校验（在 service 层实现）
