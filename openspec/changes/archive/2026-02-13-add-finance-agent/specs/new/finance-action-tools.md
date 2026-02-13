# finance-action-tools

财务人员操作工具

## Requirements

### REQ-FIN-ACTION-1: fin_admin_review_reimbursement

审核报销单：approve/reject/return。approve 时关联 BudgetUsage 并累加 Budget.used_amount。需 finance 角色。

### REQ-FIN-ACTION-2: fin_admin_process_invoice_request

处理开票申请。参数：customer, amount, description。返回开票结果。需 finance 角色。

## Scenarios

- 审核通过 → 状态改 approved，扣预算
- 审核拒绝 → 状态改 rejected
- 退回 → 状态改 returned（允许员工修改重提）
- 预算不足时审核通过需提示
