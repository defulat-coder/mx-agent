## 1. 数据模型与 Schema

- [x] 1.1 创建 `app/models/it/__init__.py`，导出所有 IT 模型
- [x] 1.2 创建 `app/models/it/asset.py`（ITAsset 模型）
- [x] 1.3 创建 `app/models/it/ticket.py`（ITTicket 模型）
- [x] 1.4 创建 `app/models/it/asset_history.py`（ITAssetHistory 模型）
- [x] 1.5 创建 `app/schemas/it.py`（ITAssetResponse / ITTicketResponse / ITTicketCreateRequest / ITTicketStatsResponse / ITAssetStatsResponse）
- [x] 1.6 在 `app/core/database.py` 的 init_db 中添加 `import app.models.it`

## 2. Service 层

- [x] 2.1 创建 `app/services/it.py`，实现员工工单查询（get_my_tickets / get_ticket_detail）
- [x] 2.2 实现员工设备查询（get_my_assets）
- [x] 2.3 实现工单创建（create_ticket，含自动生成 ticket_no）
- [x] 2.4 实现 IT 管理员工单查询（get_all_tickets，支持多条件筛选）
- [x] 2.5 实现 IT 管理员工单处理（handle_ticket：accept/resolve/close）
- [x] 2.6 实现 IT 管理员设备查询（get_all_assets，支持状态/类型筛选）
- [x] 2.7 实现设备分配（assign_asset）和回收（reclaim_asset），含写入 ITAssetHistory
- [x] 2.8 实现工单统计（ticket_stats）、设备统计（asset_stats）、故障趋势（fault_trend）

## 3. Tools 层

- [x] 3.1 创建 `app/tools/it/utils.py`（get_it_admin_id 角色校验函数）
- [x] 3.2 创建 `app/tools/it/query.py`（it_get_my_tickets / it_get_ticket_detail / it_get_my_assets）
- [x] 3.3 创建 `app/tools/it/action.py`（it_create_ticket）
- [x] 3.4 创建 `app/tools/it/admin_query.py`（it_admin_get_tickets / it_admin_get_assets / it_admin_ticket_stats / it_admin_asset_stats / it_admin_fault_trend）
- [x] 3.5 创建 `app/tools/it/admin_action.py`（it_admin_handle_ticket / it_admin_assign_asset / it_admin_reclaim_asset）
- [x] 3.6 创建 `app/tools/it/__init__.py`，按角色分组导出（it_employee_tools / it_admin_tools）

## 4. Skills 知识库

- [x] 4.1 创建 `app/skills/it/wifi-vpn/`（SKILL.md + references/policy.md）
- [x] 4.2 创建 `app/skills/it/printer/`（SKILL.md + references/policy.md）
- [x] 4.3 创建 `app/skills/it/email/`（SKILL.md + references/policy.md）
- [x] 4.4 创建 `app/skills/it/security/`（SKILL.md + references/policy.md）
- [x] 4.5 创建 `app/skills/it/device-policy/`（SKILL.md + references/policy.md）

## 5. Agent 与路由集成

- [x] 5.1 创建 `app/agents/it_agent.py`（IT Agent 定义，含 instructions 提示词）
- [x] 5.2 修改 `app/agents/router_agent.py`，members 追加 it_agent，instructions 追加 IT 路由规则

## 6. 角色扩展

- [x] 6.1 修改 `app/tools/hr/utils.py`，郑晓明 mock 数据 roles 追加 "it_admin"
- [x] 6.2 修改 `scripts/generate_token.py`，郑晓明 JWT roles 追加 "it_admin"

## 7. Mock 数据

- [x] 7.1 创建 `scripts/seed_it_data.py`，生成 ~30 条 ITAsset 数据
- [x] 7.2 生成 ~60 条 ITTicket 数据（覆盖各类型/状态/优先级，时间跨度近 3 个月）
- [x] 7.3 生成 ~15 条 ITAssetHistory 数据（分配/回收记录）
