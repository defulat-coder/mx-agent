# finance-data-models

财务数据模型 — 6 张 SQLAlchemy ORM 表 + Pydantic Schema

## Requirements

### REQ-FIN-MODEL-1: Reimbursement 模型

文件 `app/models/finance/reimbursement.py`，表名 `reimbursements`。

字段：reimbursement_no, employee_id(FK), type, amount, status, reviewer_id(FK,nullable), review_remark, reviewed_at, department_id(FK)。

### REQ-FIN-MODEL-2: ReimbursementItem 模型

文件 `app/models/finance/reimbursement_item.py`，表名 `reimbursement_items`。

字段：reimbursement_id(FK), description, amount, expense_date, category。

### REQ-FIN-MODEL-3: Budget 模型

文件 `app/models/finance/budget.py`，表名 `budgets`。

字段：department_id(FK), year, total_amount, used_amount, status。

### REQ-FIN-MODEL-4: BudgetUsage 模型

文件 `app/models/finance/budget_usage.py`，表名 `budget_usages`。

字段：budget_id(FK), reimbursement_id(FK,nullable), amount, category, description, used_date。

### REQ-FIN-MODEL-5: Payable 模型

文件 `app/models/finance/payable.py`，表名 `payables`。

字段：payable_no, vendor, amount, due_date, status, description。

### REQ-FIN-MODEL-6: Receivable 模型

文件 `app/models/finance/receivable.py`，表名 `receivables`。

字段：receivable_no, customer, amount, due_date, status, description。

### REQ-FIN-MODEL-7: __init__.py 导出

`app/models/finance/__init__.py` 导入并导出全部 6 个模型。

### REQ-FIN-MODEL-8: Pydantic Schema

`app/schemas/finance.py` 定义全部响应模型，所有字段带 `Field(description="中文说明")`。

## Scenarios

- 所有模型继承 Base（含 id / created_at / updated_at）
- Reimbursement 与 ReimbursementItem 1:N
- Budget 与 BudgetUsage 1:N
- 报销审核通过后可关联 BudgetUsage
