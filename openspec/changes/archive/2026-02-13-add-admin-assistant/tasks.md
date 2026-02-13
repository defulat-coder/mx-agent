# Tasks — add-admin-assistant

## 数据模型

- [x] 创建 `app/models/admin/meeting_room.py` — MeetingRoom 模型
- [x] 创建 `app/models/admin/room_booking.py` — RoomBooking 模型
- [x] 创建 `app/models/admin/office_supply.py` — OfficeSupply 模型
- [x] 创建 `app/models/admin/supply_request.py` — SupplyRequest 模型
- [x] 创建 `app/models/admin/express.py` — Express 模型
- [x] 创建 `app/models/admin/visitor.py` — Visitor 模型
- [x] 创建 `app/models/admin/__init__.py` — 导出全部模型
- [x] 创建 `app/schemas/admin.py` — 全部响应 Schema

## Service 层

- [x] 创建 `app/services/admin.py` — 全部业务逻辑（含 30 分钟槽位校验、冲突检测、库存扣减等）

## Tools 层

- [x] 创建 `app/tools/admin/utils.py` — get_admin_staff_id()
- [x] 创建 `app/tools/admin/query.py` — 4 个员工查询工具
- [x] 创建 `app/tools/admin/action.py` — 5 个员工操作工具
- [x] 创建 `app/tools/admin/admin_query.py` — 6 个行政人员查询工具
- [x] 创建 `app/tools/admin/admin_action.py` — 3 个行政人员管理工具
- [x] 创建 `app/tools/admin/__init__.py` — 按角色分组导出

## Skills

- [x] 创建 `app/skills/admin/travel-policy/` — SKILL.md + references/policy.md
- [x] 创建 `app/skills/admin/office-rules/` — SKILL.md + references/policy.md
- [x] 创建 `app/skills/admin/meeting-room-rules/` — SKILL.md + references/policy.md

## Agent 集成

- [x] 创建 `app/agents/admin_agent.py` — 行政 Agent 定义
- [x] 修改 `app/agents/router_agent.py` — 追加 admin_agent 成员和路由规则

## 角色扩展

- [x] 修改 `app/tools/hr/utils.py` — mock 用户追加 admin_staff 角色
- [x] 修改 `scripts/generate_token.py` — 追加 admin_staff 角色

## 数据库

- [x] 修改 `app/core/database.py` — init_db 导入行政模型

## Mock 数据

- [x] 创建 `scripts/seed_admin_data.py` — 种子脚本（~100 条）
- [x] 生成 `scripts/admin_seed.sql` — SQL 文件
- [x] 执行种子 SQL 灌入数据库
