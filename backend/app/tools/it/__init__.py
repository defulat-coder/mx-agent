"""IT 运维 Tools — 按角色分组导出"""

from app.tools.it.action import it_create_ticket
from app.tools.it.admin_action import (
    it_admin_assign_asset,
    it_admin_handle_ticket,
    it_admin_reclaim_asset,
)
from app.tools.it.admin_query import (
    it_admin_asset_stats,
    it_admin_fault_trend,
    it_admin_get_assets,
    it_admin_get_tickets,
    it_admin_ticket_stats,
)
from app.tools.it.query import it_get_my_assets, it_get_my_tickets, it_get_ticket_detail

# 员工工具（所有用户可用）
it_query_tools = [it_get_my_tickets, it_get_ticket_detail, it_get_my_assets]
it_action_tools = [it_create_ticket]
it_employee_tools = it_query_tools + it_action_tools

# IT 管理员工具
it_admin_query_tools = [
    it_admin_get_tickets,
    it_admin_get_assets,
    it_admin_ticket_stats,
    it_admin_asset_stats,
    it_admin_fault_trend,
]
it_admin_action_tools = [it_admin_handle_ticket, it_admin_assign_asset, it_admin_reclaim_asset]
it_admin_tools = it_admin_query_tools + it_admin_action_tools

__all__ = [
    "it_employee_tools",
    "it_admin_tools",
]
