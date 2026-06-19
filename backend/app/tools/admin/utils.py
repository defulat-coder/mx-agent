"""行政 Tools 辅助函数 — 从 RunContext 提取行政人员身份"""

from agno.run import RunContext

from app.tools.hr.utils import get_employee_id


def get_admin_staff_id(run_context: RunContext) -> int:
    """从 session_state 提取行政人员身份并校验角色。

    Returns:
        行政人员的员工 ID

    Raises:
        ValueError: 非行政人员角色
    """
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    roles: list[str] = state.get("roles", [])  # type: ignore[union-attr]
    if "admin_staff" not in roles:
        raise ValueError("该功能仅限行政人员使用")
    return employee_id
