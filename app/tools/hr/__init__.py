"""HR Tools — 统一导出查询、办理、主管、管理者、人才发展工具"""

from app.tools.hr.action import apply_leave, apply_overtime, apply_reimbursement
from app.tools.hr.admin_action import (
    admin_approve_leave_request,
    admin_approve_overtime_request,
)
from app.tools.hr.admin_query import (
    admin_get_all_attendance,
    admin_get_all_employees,
    admin_get_all_leave_requests,
    admin_get_all_overtime_records,
    admin_get_attendance_summary,
    admin_get_department_headcount,
    admin_get_employee_profile,
    admin_get_employee_salary,
    admin_get_employee_social_insurance,
    admin_get_leave_summary,
    admin_get_salary_summary,
)
from app.tools.hr.manager_action import approve_leave_request, approve_overtime_request
from app.tools.hr.talent_dev_query import (
    td_get_employee_attendance,
    td_get_employee_certificates,
    td_get_employee_education,
    td_get_employee_history,
    td_get_employee_idp,
    td_get_employee_performance,
    td_get_employee_profile,
    td_get_employee_projects,
    td_get_employee_skills,
    td_get_employee_talent_review,
    td_get_employee_training,
    td_idp_summary,
    td_nine_grid_distribution,
    td_performance_distribution,
    td_promotion_stats,
    td_training_summary,
    td_turnover_analysis,
)
from app.tools.hr.discovery import (
    td_assess_flight_risk,
    td_discover_hidden_talent,
    td_find_candidates,
    td_promotion_readiness,
    td_talent_portrait,
    td_team_capability_gap,
)
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

admin_query_tools = [
    admin_get_all_employees,
    admin_get_employee_salary,
    admin_get_employee_social_insurance,
    admin_get_employee_profile,
    admin_get_all_leave_requests,
    admin_get_all_attendance,
    admin_get_all_overtime_records,
    admin_get_department_headcount,
    admin_get_attendance_summary,
    admin_get_salary_summary,
    admin_get_leave_summary,
]

admin_action_tools = [
    admin_approve_leave_request,
    admin_approve_overtime_request,
]

admin_tools = admin_query_tools + admin_action_tools

talent_dev_tools = [
    td_get_employee_profile,
    td_get_employee_training,
    td_get_employee_talent_review,
    td_get_employee_idp,
    td_get_employee_performance,
    td_get_employee_history,
    td_get_employee_attendance,
    td_get_employee_skills,
    td_get_employee_education,
    td_get_employee_projects,
    td_get_employee_certificates,
    td_training_summary,
    td_nine_grid_distribution,
    td_performance_distribution,
    td_turnover_analysis,
    td_promotion_stats,
    td_idp_summary,
]

discovery_tools = [
    td_discover_hidden_talent,
    td_assess_flight_risk,
    td_promotion_readiness,
    td_find_candidates,
    td_talent_portrait,
    td_team_capability_gap,
]

all_tools = employee_tools + manager_tools + admin_tools + talent_dev_tools + discovery_tools
