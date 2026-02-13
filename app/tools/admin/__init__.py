"""行政管理 Tools — 按角色分组导出"""

from app.tools.admin.action import (
    adm_apply_travel,
    adm_book_room,
    adm_book_visitor,
    adm_cancel_booking,
    adm_request_supply,
)
from app.tools.admin.admin_action import (
    adm_admin_approve_supply,
    adm_admin_register_express,
    adm_admin_release_room,
)
from app.tools.admin.admin_query import (
    adm_admin_get_all_bookings,
    adm_admin_get_all_express,
    adm_admin_get_supply_requests,
    adm_admin_get_supply_stock,
    adm_admin_get_visitors,
    adm_admin_usage_stats,
)
from app.tools.admin.query import (
    adm_get_available_rooms,
    adm_get_my_bookings,
    adm_get_my_express,
    adm_get_my_visitors,
)

# 员工工具（所有用户可用）
adm_query_tools = [adm_get_available_rooms, adm_get_my_bookings, adm_get_my_express, adm_get_my_visitors]
adm_action_tools = [adm_book_room, adm_cancel_booking, adm_request_supply, adm_book_visitor, adm_apply_travel]
adm_employee_tools = adm_query_tools + adm_action_tools

# 行政管理员工具
adm_admin_query_tools = [
    adm_admin_get_all_bookings,
    adm_admin_get_supply_requests,
    adm_admin_get_supply_stock,
    adm_admin_get_all_express,
    adm_admin_get_visitors,
    adm_admin_usage_stats,
]
adm_admin_action_tools = [adm_admin_release_room, adm_admin_approve_supply, adm_admin_register_express]
adm_admin_tools = adm_admin_query_tools + adm_admin_action_tools

__all__ = [
    "adm_employee_tools",
    "adm_admin_tools",
]
