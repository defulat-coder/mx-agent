## Context

系统已有 HR/IT/行政 三个子 Agent。Finance Agent 已有占位文件，需替换为完整实现。

## Goals / Non-Goals

**Goals:**
- 3 个角色：员工、主管（预算负责人）、财务人员
- 6 张表完整建模
- 个税查询跨域复用 HR SalaryRecord
- 去掉发票验真功能（不对接外部税务系统）
- 主管复用 manager 角色作为预算负责人
- 100 条 Mock 数据

**Non-Goals:**
- 不对接外部税务/银行系统
- 不实现发票验真/OCR
- 不实现实际付款/收款流程
- 不新增 budget_owner 角色

## Decisions

### 1. 数据模型

6 张表（去掉 Invoice，发票验真不做）。

Reimbursement:
- `reimbursement_no`: String(32), unique, index, comment="报销单号"
- `employee_id`: FK → employees.id, comment="申请人 ID"
- `type`: String(32), comment="报销类型"（差旅/餐费/交通/办公/招待/其他）
- `amount`: Float, comment="报销金额"
- `status`: String(16), default="pending", comment="状态"（pending/approved/rejected/returned/paid）
- `reviewer_id`: FK → employees.id, nullable, comment="审核人 ID"
- `review_remark`: String(256), default="", comment="审核备注"
- `reviewed_at`: DateTime, nullable, comment="审核时间"
- `department_id`: FK → departments.id, comment="部门 ID"

ReimbursementItem:
- `reimbursement_id`: FK → reimbursements.id, comment="报销单 ID"
- `description`: String(256), comment="费用说明"
- `amount`: Float, comment="金额"
- `expense_date`: Date, comment="费用日期"
- `category`: String(32), comment="费用科目"

Budget:
- `department_id`: FK → departments.id, comment="部门 ID"
- `year`: Integer, comment="年度"
- `total_amount`: Float, comment="预算总额"
- `used_amount`: Float, default=0, comment="已使用金额"
- `status`: String(16), default="active", comment="状态"

BudgetUsage:
- `budget_id`: FK → budgets.id, comment="预算 ID"
- `reimbursement_id`: FK → reimbursements.id, nullable, comment="关联报销单"
- `amount`: Float, comment="使用金额"
- `category`: String(32), comment="费用科目"
- `description`: String(256), default="", comment="说明"
- `used_date`: Date, comment="使用日期"

Payable:
- `payable_no`: String(32), unique, index, comment="应付单号"
- `vendor`: String(128), comment="供应商"
- `amount`: Float, comment="金额"
- `due_date`: Date, comment="到期日"
- `status`: String(16), comment="状态"（pending/paid/overdue）
- `description`: String(256), default="", comment="说明"

Receivable:
- `receivable_no`: String(32), unique, index, comment="应收单号"
- `customer`: String(128), comment="客户"
- `amount`: Float, comment="金额"
- `due_date`: Date, comment="到期日"
- `status`: String(16), comment="状态"（pending/received/overdue）
- `description`: String(256), default="", comment="说明"

### 2. 角色与权限

新增 `finance` 角色。主管复用 `manager` 角色作为部门预算负责人。

### 3. 工具命名

员工：`fin_` 前缀，主管：`fin_mgr_` 前缀，财务人员：`fin_admin_` 前缀。

| 文件 | 工具 |
|------|------|
| query.py | fin_get_my_reimbursements, fin_get_reimbursement_detail, fin_get_department_budget, fin_get_my_tax |
| manager_query.py | fin_mgr_get_budget_overview, fin_mgr_get_expense_detail, fin_mgr_get_budget_alert |
| admin_query.py | fin_admin_get_all_reimbursements, fin_admin_get_expense_summary, fin_admin_get_budget_analysis, fin_admin_get_payables, fin_admin_get_receivables |
| admin_action.py | fin_admin_review_reimbursement, fin_admin_process_invoice_request |

### 4. 个税查询

跨域读 HR 的 `SalaryRecord` 表，提取 `tax` 字段。Service 层直接导入 HR 模型查询。

### 5. Skills

| 目录 | 内容 |
|------|------|
| reimbursement-policy/ | 报销标准（差旅/餐费/交通限额、审批流程、发票要求） |
| budget-rules/ | 预算制度（编制/执行/调整流程、超支审批） |
| tax-knowledge/ | 税务知识（个税计算规则、专项附加扣除） |

### 6. Mock 数据

| 表 | 数量 |
|----|------|
| Reimbursement | 20 |
| ReimbursementItem | 40 |
| Budget | 10 |
| BudgetUsage | 15 |
| Payable | 10 |
| Receivable | 5 |

## Risks / Trade-offs

- **[权衡] 跨域读 HR 数据** → 财务 service 直接导入 HR 模型，耦合但简单，后续可加服务间接口
- **[权衡] 不做发票验真** → 简化实现，后续可扩展
- **[权衡] manager 复用为预算负责人** → 不一定所有主管管预算，但简化角色体系
