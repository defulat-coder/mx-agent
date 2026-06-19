"""法务管理 Tools — 按角色分组导出"""

from app.tools.legal.admin_action import (
    leg_admin_analyze_contract,
    leg_admin_review_contract,
)
from app.tools.legal.admin_query import (
    leg_admin_get_contracts,
    leg_admin_get_expiring,
    leg_admin_get_stats,
)
from app.tools.legal.query import (
    leg_get_my_contracts,
    leg_get_template_download,
    leg_get_templates,
)

# 员工工具（所有用户可用）
leg_employee_tools = [
    leg_get_templates,
    leg_get_template_download,
    leg_get_my_contracts,
]

# 法务人员工具
leg_admin_tools = [
    leg_admin_get_contracts,
    leg_admin_review_contract,
    leg_admin_get_expiring,
    leg_admin_analyze_contract,
    leg_admin_get_stats,
]

__all__ = [
    "leg_employee_tools",
    "leg_admin_tools",
]
