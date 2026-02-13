## Context

系统已有 HR + IT 两个子 Agent，基础设施完备。行政助手复用全部基础设施，新增行政业务域。

## Goals / Non-Goals

**Goals:**
- 5 个子域全覆盖：会议室预订、办公用品申领、快递收发、访客预约、差旅申请
- 会议室预订采用 30 分钟槽位制，含时间冲突检测
- 差旅申请复用审批链接模式（不建表）
- 100 条 Mock 数据

**Non-Goals:**
- 不对接外部会议室/日历系统
- 不实现真实快递物流追踪
- 不实现差旅的机票/酒店对接
- 不实现办公用品采购流程（仅申领和库存查询）

## Decisions

### 1. 数据模型

6 张表，差旅申请不建表（审批链接模式）。

MeetingRoom:
- `name`: String(64), comment="会议室名称"
- `floor`: String(16), comment="楼层"
- `capacity`: Integer, comment="容纳人数"
- `equipment`: String(256), default="", comment="设备（投影/白板/视频等）"
- `status`: String(16), default="available", comment="状态"（available/maintenance）

RoomBooking:
- `room_id`: FK → meeting_rooms.id
- `employee_id`: FK → employees.id
- `title`: String(128), comment="会议主题"
- `start_time`: DateTime, comment="开始时间"（30 分钟对齐）
- `end_time`: DateTime, comment="结束时间"（30 分钟对齐）
- `status`: String(16), default="active", comment="状态"（active/cancelled/completed）

OfficeSupply:
- `name`: String(64), comment="用品名称"
- `category`: String(32), comment="分类"（文具/耗材/清洁/其他）
- `stock`: Integer, comment="库存数量"
- `unit`: String(16), comment="单位"

SupplyRequest:
- `employee_id`: FK → employees.id
- `items`: Text, comment="申领物品（JSON 格式）"
- `status`: String(16), default="pending", comment="状态"（pending/approved/rejected）
- `approved_by`: FK → employees.id, nullable
- `remark`: String(256), default=""

Express:
- `tracking_no`: String(64), unique, comment="快递单号"
- `type`: String(16), comment="类型"（receive/send）
- `employee_id`: FK → employees.id
- `courier`: String(32), comment="快递公司"
- `status`: String(16), comment="状态"（pending/picked_up/sent）
- `received_at`: DateTime, nullable
- `remark`: String(256), default=""

Visitor:
- `visitor_name`: String(64), comment="访客姓名"
- `company`: String(128), default="", comment="来访单位"
- `phone`: String(32), default="", comment="联系电话"
- `host_id`: FK → employees.id, comment="接待人 ID"
- `visit_date`: Date, comment="来访日期"
- `visit_time`: String(16), default="", comment="来访时间段"
- `purpose`: String(256), default="", comment="来访目的"
- `status`: String(16), default="pending", comment="状态"（pending/checked_in/checked_out/cancelled）

### 2. 会议室 30 分钟槽位

- start_time 和 end_time 必须是 30 分钟的整数倍（:00 或 :30）
- 预订前校验时间段内该会议室无 active 状态的预订
- 最多提前 7 天预订
- 开始前 30 分钟可取消

### 3. 角色与权限

新增 `admin_staff` 角色，`app/tools/admin/utils.py` 提供 `get_admin_staff_id()`。

### 4. 工具命名

员工：`adm_` 前缀，行政人员：`adm_admin_` 前缀。

| 文件 | 工具 |
|------|------|
| query.py | adm_get_available_rooms, adm_get_my_bookings, adm_get_my_express, adm_get_my_visitors |
| action.py | adm_book_room, adm_cancel_booking, adm_request_supply, adm_book_visitor, adm_apply_travel |
| admin_query.py | adm_admin_get_all_bookings, adm_admin_get_supply_requests, adm_admin_get_supply_stock, adm_admin_get_all_express, adm_admin_get_visitors, adm_admin_usage_stats |
| admin_action.py | adm_admin_release_room, adm_admin_approve_supply, adm_admin_register_express |

### 5. Skills

| 目录 | 内容 |
|------|------|
| travel-policy/ | 差旅标准（交通/住宿/餐费标准） |
| office-rules/ | 办公规范（公共区域/工位管理） |
| meeting-room-rules/ | 会议室使用规范（预订/取消/超时规则） |

### 6. Mock 数据

| 表 | 数量 |
|----|------|
| MeetingRoom | 10 |
| RoomBooking | 30 |
| OfficeSupply | 15 |
| SupplyRequest | 15 |
| Express | 15 |
| Visitor | 15 |

## Risks / Trade-offs

- **[风险] 会议室冲突检测在高并发下可能有竞态** → 当前 SQLite 单写问题不大，生产环境需加数据库锁
- **[权衡] 差旅不建表** → 简单但无法查询历史差旅，后续可按需扩展
- **[权衡] 办公用品 items 用 JSON 而非子表** → 简化模型，牺牲查询灵活性
