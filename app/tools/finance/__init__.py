"""财务管理 Tools — 按角色分组导出"""

from app.tools.finance.admin_action import (
    fin_admin_process_invoice_request,
    fin_admin_review_reimbursement,
)
from app.tools.finance.admin_query import (
    fin_admin_get_all_reimbursements,
    fin_admin_get_budget_analysis,
    fin_admin_get_expense_summary,
    fin_admin_get_payables,
    fin_admin_get_receivables,
)
from app.tools.finance.manager_query import (
    fin_mgr_get_budget_alert,
    fin_mgr_get_budget_overview,
    fin_mgr_get_expense_detail,
)
from app.tools.finance.query import (
    fin_get_department_budget,
    fin_get_my_reimbursements,
    fin_get_my_tax,
    fin_get_reimbursement_detail,
)

# 员工工具（所有用户可用）
fin_employee_tools = [
    fin_get_my_reimbursements,
    fin_get_reimbursement_detail,
    fin_get_department_budget,
    fin_get_my_tax,
]

# 主管工具（manager 角色 = 部门预算负责人）
fin_manager_tools = [
    fin_mgr_get_budget_overview,
    fin_mgr_get_expense_detail,
    fin_mgr_get_budget_alert,
]

# 财务人员工具
fin_admin_query_tools = [
    fin_admin_get_all_reimbursements,
    fin_admin_get_expense_summary,
    fin_admin_get_budget_analysis,
    fin_admin_get_payables,
    fin_admin_get_receivables,
]
fin_admin_action_tools = [
    fin_admin_review_reimbursement,
    fin_admin_process_invoice_request,
]
fin_admin_tools = fin_admin_query_tools + fin_admin_action_tools

__all__ = [
    "fin_employee_tools",
    "fin_manager_tools",
    "fin_admin_tools",
]
