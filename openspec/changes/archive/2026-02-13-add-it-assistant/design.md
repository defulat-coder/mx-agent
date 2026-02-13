## Context

当前系统已有 HR/财务/法务三个子 Agent，通过 Router Team 统一路由。基础设施完备：JWT 认证、角色校验（get_xxx_id 模式）、SQLite 异步会话、Skills 知识库、脱敏日志。

IT 助手需完全复用现有基础设施，新增 IT 业务域的模型、服务、工具和 Agent。

## Goals / Non-Goals

**Goals:**
- 新增 IT 运维 Agent，支持员工自助（工单/设备查询、工单创建）和 IT 管理员（工单处理、设备管理、统计报表）
- 设备管理达 L2 级别（查询 + 分配/回收，含流转历史）
- IT FAQ 使用 Skills 知识库（markdown），结构化数据使用 SQLite
- 100 条 Mock 数据覆盖各类型工单和设备
- 无缝集成到 Router Team

**Non-Goals:**
- 不对接外部工单系统（Jira/飞书），自建 SQLite
- 不实现真实的密码重置/权限开通等操作，仅生成工单
- 不实现设备 L3（采购、折旧、生命周期管理）
- 不实现工单审批链（单级处理即可）

## Decisions

### 1. 数据模型设计

**选择**：3 张表（ITAsset + ITTicket + ITAssetHistory），与 HR 模型同库但独立 `app/models/it/` 目录。

**理由**：
- 与 HR 模型保持一致的组织方式
- ITAssetHistory 单独建表而非放 JSON 字段，便于查询设备流转记录
- 工单不需要子表（明细行），单表即可覆盖所有工单类型

**表设计要点**：

ITAsset:
- `asset_no` 唯一索引（格式 `IT-A-xxxx`）
- `type`: laptop / desktop / monitor / peripheral / other
- `status`: idle（空闲）/ in_use（使用中）/ maintenance（维修中）/ scrapped（报废）
- `employee_id` FK → employees.id（nullable，空闲/报废时为 null）
- 含 brand、model_name、purchase_date、warranty_expire

ITTicket:
- `ticket_no` 唯一索引（格式 `IT-T-xxxx`）
- `type`: repair（报修）/ password_reset（密码重置）/ software_install（软件安装）/ permission（权限申请）/ other
- `status`: open（待处理）/ in_progress（处理中）/ resolved（已解决）/ closed（已关闭）
- `priority`: low / medium / high / urgent
- `submitter_id` FK → employees.id
- `handler_id` FK → employees.id（nullable，未分配时为 null）
- 含 title、description、resolution、resolved_at

ITAssetHistory:
- `action`: assign（分配）/ reclaim（回收）/ transfer（调拨）
- `asset_id` FK → it_assets.id
- `from_employee_id` / `to_employee_id`（nullable）
- `operated_by` FK → employees.id

### 2. 角色与权限

**选择**：新增 `it_admin` 角色，复用 `get_employee_id` + 新增 `get_it_admin_id` 校验函数。

**理由**：与 HR 的 `get_admin_id` / `get_talent_dev_id` 完全一致的模式。

**放置位置**：`app/tools/it/utils.py`，从公共的 `app/tools/hr/utils.py` 导入 `get_employee_id`。

### 3. 工具命名与分组

**选择**：员工工具 `it_` 前缀，管理员工具 `it_admin_` 前缀。

| 文件 | 工具 |
|------|------|
| query.py | it_get_my_tickets, it_get_ticket_detail, it_get_my_assets |
| action.py | it_create_ticket |
| admin_query.py | it_admin_get_tickets, it_admin_get_assets, it_admin_ticket_stats, it_admin_asset_stats, it_admin_fault_trend |
| admin_action.py | it_admin_handle_ticket, it_admin_assign_asset, it_admin_reclaim_asset |

共 12 个工具。

### 4. Skills 知识库

**选择**：5 个 Skills 放在 `app/skills/it/` 目录，与 HR Skills 结构一致。

| Skill 目录 | 内容 |
|------------|------|
| wifi-vpn/ | WiFi 连接、VPN 配置、常见故障排查 |
| printer/ | 打印机安装、驱动问题、常见故障 |
| email/ | 邮箱配置（Outlook/手机）、常见问题 |
| security/ | 信息安全制度、密码策略、数据保护 |
| device-policy/ | 设备使用规范、借用归还流程 |

每个目录含 `SKILL.md` + `references/policy.md`。

### 5. Mock 数据策略

**选择**：Python 种子脚本 `scripts/seed_it_data.py`，约 100 条数据。

分布：
- ITAsset ~30 条：覆盖各类型和状态，分配给不同部门员工
- ITTicket ~60 条：覆盖各类型/状态/优先级，时间跨度近 3 个月
- ITAssetHistory ~15 条：分配和回收记录

### 6. Agent 集成

**选择**：`app/agents/it_agent.py` 定义 IT Agent，在 `router_agent.py` 的 members 中追加。

Agent instructions 包含：
- 员工自助能力说明
- IT 管理员权限说明
- 工具与角色对应关系
- 行为准则（不编造数据、权限错误不重试等）

Router instructions 追加：
- "IT 运维相关问题（设备报修、密码重置、权限申请、软件安装、设备查询等）→ IT Assistant"

## Risks / Trade-offs

- **[风险] 工具数量增加导致 LLM 选择困难** → 通过 Router Team 路由隔离，IT Agent 只看到 IT 工具，不影响 HR Agent
- **[风险] Mock 数据与真实员工 ID 对不上** → 种子脚本引用 employees 表已有数据，确保 FK 一致
- **[权衡] 员工工单与管理员工单用同一张表** → 通过 submitter_id 过滤实现权限隔离，简单高效
- **[权衡] utils.py 放在 tools/it/ 而非公共位置** → IT 角色校验逻辑专属 IT 域，不污染 HR utils
