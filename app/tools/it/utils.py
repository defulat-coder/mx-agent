"""IT Tools 辅助函数 — 从 RunContext 提取 IT 管理员身份"""

from agno.run import RunContext

from app.tools.hr.utils import get_employee_id


def get_it_admin_id(run_context: RunContext) -> int:
    """从 session_state 提取 IT 管理员身份并校验角色。

    Returns:
        IT 管理员的员工 ID

    Raises:
        ValueError: 非 IT 管理员角色
    """
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    roles: list[str] = state.get("roles", [])  # type: ignore[union-attr]
    if "it_admin" not in roles:
        raise ValueError("该功能仅限 IT 管理员使用")
    return employee_id
