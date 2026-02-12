"""HR Tools — 统一导出查询、办理、主管工具"""

from app.tools.hr.action import apply_leave, apply_overtime, apply_reimbursement
from app.tools.hr.manager_action import approve_leave_request, approve_overtime_request
from app.tools.hr.manager_query import (
    get_employee_profile,
    get_team_attendance,
    get_team_leave_balances,
    get_team_leave_requests,
    get_team_members,
    get_team_overtime_records,
)
from app.tools.hr.query import (
    get_attendance,
    get_employee_info,
    get_leave_balance,
    get_leave_requests,
    get_overtime_records,
    get_salary_records,
    get_social_insurance,
)

query_tools = [
    get_employee_info,
    get_salary_records,
    get_social_insurance,
    get_attendance,
    get_leave_balance,
    get_leave_requests,
    get_overtime_records,
]

action_tools = [
    apply_leave,
    apply_overtime,
    apply_reimbursement,
]

employee_tools = query_tools + action_tools

manager_query_tools = [
    get_team_members,
    get_team_attendance,
    get_team_leave_requests,
    get_team_leave_balances,
    get_team_overtime_records,
    get_employee_profile,
]

manager_action_tools = [
    approve_leave_request,
    approve_overtime_request,
]

manager_tools = manager_query_tools + manager_action_tools

all_tools = employee_tools + manager_tools
