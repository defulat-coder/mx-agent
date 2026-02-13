"""财务 Tools 辅助函数 — 从 RunContext 提取财务人员身份"""

from agno.run import RunContext

from app.tools.hr.utils import get_employee_id


def get_finance_id(run_context: RunContext) -> int:
    """从 session_state 提取财务人员身份并校验角色。

    Returns:
        财务人员的员工 ID

    Raises:
        ValueError: 非财务人员角色
    """
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    roles: list[str] = state.get("roles", [])  # type: ignore[union-attr]
    if "finance" not in roles:
        raise ValueError("该功能仅限财务人员使用")
    return employee_id
