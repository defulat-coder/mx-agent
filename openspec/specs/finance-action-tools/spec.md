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
- 预算缺失、冻结或余额不足时审核失败，报销状态与预算均保持不变
- 重复或并发审核仅允许一次成功，同一报销单最多生成一条 BudgetUsage
- 开票工具只准备 OA 确认链接，不得在未调用真实开票系统时声称已开具
