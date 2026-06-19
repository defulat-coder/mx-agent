"""法务 Tools 辅助函数 — 从 RunContext 提取法务人员身份"""

from agno.run import RunContext

from app.tools.hr.utils import get_employee_id


def get_legal_id(run_context: RunContext) -> int:
    """从 session_state 提取法务人员身份并校验角色。

    Returns:
        法务人员的员工 ID

    Raises:
        ValueError: 非法务人员角色
    """
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    roles: list[str] = state.get("roles", [])  # type: ignore[union-attr]
    if "legal" not in roles:
        raise ValueError("该功能仅限法务人员使用")
    return employee_id
