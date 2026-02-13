## Why

员工日常行政需求（会议室预订、办公用品申领、快递查询、访客预约、差旅申请）缺乏统一入口，需新增行政助手与 HR/IT 助手并列，通过 Router Team 统一路由。

## What Changes

- 新增行政 Agent，支持员工自助和行政人员两个角色
- 新增 6 张数据表：MeetingRoom / RoomBooking / OfficeSupply / SupplyRequest / Express / Visitor
- 新增 17 个 Tools：员工 8 个 + 行政人员 9 个
- 新增 3 个 Skills：差旅标准、办公规范、会议室使用规范
- 新增 `admin_staff` 角色到权限体系
- 会议室预订采用 30 分钟槽位制，含时间冲突检测
- 差旅申请不建表，复用审批链接模式
- Router Team 追加 Admin Agent 成员和路由规则
- Mock 数据种子脚本（~100 条测试数据）

## Capabilities

### New Capabilities
- `admin-data-models`: 行政数据模型（6 张表）及对应 Schema
- `admin-query-tools`: 员工行政查询工具（预订/快递/访客查询）
- `admin-action-tools`: 员工操作 + 行政人员管理（预订/申领/审批/释放/登记/统计）
- `admin-agent-impl`: 行政 Agent 定义、Skills 知识库、挂载到 Router Team

### Modified Capabilities
- `auth`: 新增 `admin_staff` 角色标识，扩展 JWT claims 和 mock 用户数据
- `router-agent`: members 追加 Admin Agent，instructions 增加行政路由规则
- `database`: init_db 中导入行政模型触发建表

## Impact

- **新增目录**：`app/models/admin/`、`app/tools/admin/`、`app/skills/admin/`、`app/schemas/admin.py`、`app/services/admin.py`、`app/agents/admin_agent.py`
- **修改文件**：`app/agents/router_agent.py`、`app/tools/hr/utils.py`（加 admin_staff mock）、`app/core/database.py`（导入行政模型）、`scripts/generate_token.py`（加 admin_staff 角色）
- **新增依赖**：无
