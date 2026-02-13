# Tasks — add-finance-agent

## 数据模型

- [x] 创建 `app/models/finance/reimbursement.py` — Reimbursement 模型
- [x] 创建 `app/models/finance/reimbursement_item.py` — ReimbursementItem 模型
- [x] 创建 `app/models/finance/budget.py` — Budget 模型
- [x] 创建 `app/models/finance/budget_usage.py` — BudgetUsage 模型
- [x] 创建 `app/models/finance/payable.py` — Payable 模型
- [x] 创建 `app/models/finance/receivable.py` — Receivable 模型
- [x] 创建 `app/models/finance/__init__.py` — 导出全部模型
- [x] 创建 `app/schemas/finance.py` — 全部响应 Schema

## Service 层

- [x] 创建 `app/services/finance.py` — 全部业务逻辑（含跨域读 HR SalaryRecord、预算扣减等）

## Tools 层

- [x] 创建 `app/tools/finance/utils.py` — get_finance_id()
- [x] 创建 `app/tools/finance/query.py` — 4 个员工查询工具
- [x] 创建 `app/tools/finance/manager_query.py` — 3 个主管查询工具
- [x] 创建 `app/tools/finance/admin_query.py` — 5 个财务人员查询工具
- [x] 创建 `app/tools/finance/admin_action.py` — 2 个财务人员操作工具
- [x] 创建 `app/tools/finance/__init__.py` — 按角色分组导出

## Skills

- [x] 创建 `app/skills/finance/reimbursement-policy/` — SKILL.md + references/policy.md
- [x] 创建 `app/skills/finance/budget-rules/` — SKILL.md + references/policy.md
- [x] 创建 `app/skills/finance/tax-knowledge/` — SKILL.md + references/policy.md

## Agent 集成

- [x] 替换 `app/agents/finance_agent.py` — 完整财务 Agent 定义
- [x] 修改 `app/agents/router_agent.py` — 更新路由规则

## 角色扩展

- [x] 修改 `app/tools/hr/utils.py` — mock 用户追加 finance 角色
- [x] 修改 `scripts/generate_token.py` — 追加 finance 角色

## 数据库

- [x] 修改 `app/core/database.py` — init_db 导入财务模型

## Mock 数据

- [x] 创建 `scripts/seed_finance_data.py` — 种子脚本（~100 条）
- [x] 生成 `scripts/finance_seed.sql` — SQL 文件
- [x] 执行种子 SQL 灌入数据库
