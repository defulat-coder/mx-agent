# finance-query-tools

员工/主管/财务人员查询工具

## Requirements

### REQ-FIN-QUERY-1: fin_get_my_reimbursements

查询当前员工的报销单列表。参数：status（可选）。

### REQ-FIN-QUERY-2: fin_get_reimbursement_detail

查询报销单详情（含明细行）。参数：reimbursement_id。员工只能查自己的。

### REQ-FIN-QUERY-3: fin_get_department_budget

查询所在部门当年预算余额。无需额外角色。

### REQ-FIN-QUERY-4: fin_get_my_tax

查询个人所得税明细。跨域读 HR SalaryRecord，提取 tax 字段。参数：year_month（可选）。

### REQ-FIN-QUERY-5: fin_mgr_get_budget_overview

主管查看本部门预算总览（总额/已用/余额/执行率）。需 manager 角色。

### REQ-FIN-QUERY-6: fin_mgr_get_expense_detail

主管查看部门费用明细。参数：category, year_month（可选）。需 manager 角色。

### REQ-FIN-QUERY-7: fin_mgr_get_budget_alert

主管查看部门预算预警（执行率超 80%）。需 manager 角色。

### REQ-FIN-QUERY-8: fin_admin_get_all_reimbursements

财务人员查询全部报销单。参数：status, type, department_id（均可选）。需 finance 角色。

### REQ-FIN-QUERY-9: fin_admin_get_expense_summary

财务人员费用汇总报表（按部门/科目/月度）。需 finance 角色。

### REQ-FIN-QUERY-10: fin_admin_get_budget_analysis

财务人员全公司预算执行分析。需 finance 角色。

### REQ-FIN-QUERY-11: fin_admin_get_payables

财务人员查询应付款。参数：status（可选）。需 finance 角色。

### REQ-FIN-QUERY-12: fin_admin_get_receivables

财务人员查询应收款。参数：status（可选）。需 finance 角色。

## Scenarios

- 员工工具通过 get_employee_id 获取身份
- 主管工具通过 get_manager_info 获取身份和部门
- 财务工具通过 get_finance_id 校验角色
- 个税查询跨域读 HR SalaryRecord
