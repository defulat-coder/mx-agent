## Why

员工报销查询、预算管理、财务审核等场景缺乏统一入口，当前 Finance Agent 仅为占位。需实现完整财务助手，与 HR/IT/行政助手并列。

## What Changes

- 替换占位 Finance Agent 为完整实现
- 新增 6 张数据表：Reimbursement / ReimbursementItem / Budget / BudgetUsage / Payable / Receivable
- 新增 14 个 Tools：员工 4 + 主管 3 + 财务人员 7
- 新增 3 个 Skills：报销政策、预算制度、税务知识
- 新增 `finance` 角色到权限体系
- 个税查询复用 HR SalaryRecord，部门预算负责人复用 manager 角色
- Router Team 更新路由规则描述
- Mock 数据种子脚本（~100 条）

## Capabilities

### New Capabilities
- `finance-data-models`: 财务数据模型（6 张表）及对应 Schema
- `finance-query-tools`: 员工/主管/财务人员查询工具
- `finance-action-tools`: 财务人员审核、开票处理
- `finance-agent-impl`: 财务 Agent 定义、Skills 知识库

### Modified Capabilities
- `auth`: 新增 `finance` 角色标识，扩展 mock 用户数据
- `router-agent`: 更新 Finance Agent 描述为已上线，增加路由规则细化
- `database`: init_db 中导入财务模型触发建表

## Impact

- **修改文件**：`app/agents/finance_agent.py`（替换占位）、`app/agents/router_agent.py`、`app/tools/hr/utils.py`、`app/core/database.py`、`scripts/generate_token.py`
- **新增目录**：`app/models/finance/`、`app/tools/finance/`、`app/skills/finance/`、`app/schemas/finance.py`、`app/services/finance.py`
- **新增依赖**：无
