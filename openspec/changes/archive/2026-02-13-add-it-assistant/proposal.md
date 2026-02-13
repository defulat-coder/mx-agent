## Why

企业员工 IT 相关需求（设备报修、密码重置、权限申请、设备查询等）目前缺乏统一入口，需要新增 IT 运维助手，与现有 HR/财务/法务助手并列，通过 Router Team 统一路由。

## What Changes

- 新增 IT 运维 Agent，支持员工自助和 IT 管理员两个角色
- 新增 3 张数据表：ITAsset（设备资产）、ITTicket（IT 工单）、ITAssetHistory（设备流转记录）
- 新增 12 个 Tools：员工工单/设备查询 4 个 + IT 管理员工单处理/设备管理/统计 8 个
- 新增 5 个 Skills：WiFi/VPN、打印机、邮箱、信息安全、设备管理规范
- 新增 `it_admin` 角色到权限体系
- Router Team 追加 IT Agent 成员和路由规则
- Mock 数据种子脚本（~100 条测试数据）

## Capabilities

### New Capabilities
- `it-data-models`: IT 运维数据模型（ITAsset / ITTicket / ITAssetHistory）及对应 Schema
- `it-query-tools`: IT 员工自助查询工具（工单查询、设备查询）
- `it-action-tools`: IT 工单创建 + IT 管理员工单处理/设备分配回收
- `it-agent-impl`: IT Agent 定义、Skills 知识库、挂载到 Router Team

### Modified Capabilities
- `auth`: 新增 `it_admin` 角色标识，扩展 JWT claims 和 mock 用户数据
- `router-agent`: members 追加 IT Agent，instructions 增加 IT 运维路由规则
- `database`: init_db 中导入 IT 模型触发建表

## Impact

- **新增目录**：`app/models/it/`、`app/tools/it/`、`app/skills/it/`、`app/schemas/it.py`、`app/services/it.py`、`app/agents/it_agent.py`
- **修改文件**：`app/agents/router_agent.py`、`app/tools/hr/utils.py`（加 it_admin mock）、`app/core/database.py`（导入 IT 模型）、`scripts/generate_token.py`（加 it_admin 角色）
- **新增依赖**：无（复用现有 SQLAlchemy + agno 基础设施）
