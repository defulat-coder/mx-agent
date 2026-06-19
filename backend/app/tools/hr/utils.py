"""HR Tools 辅助函数 — 从 RunContext 安全提取身份信息"""

from agno.run import RunContext
from loguru import logger

from app.config import settings

# 模拟员工数据，用于 os.agno.com 等无 JWT 场景的调试
_MOCK_EMPLOYEES = [
    # {"employee_id": 1, "roles": ["manager"], "department_id": 7, "_name": "张三（后端组长）"},
    # {"employee_id": 2, "roles": [], "department_id": 7, "_name": "李四（后端工程师）"},
    {"employee_id": 9, "roles": ["manager", "admin", "talent_dev", "it_admin", "admin_staff", "finance", "legal"], "department_id": 2, "_name": "郑晓明（技术总监/管理者/人才发展/IT管理员/行政/财务/法务）"},
    {"employee_id": 5, "roles": [], "department_id": 3, "_name": "钱七（产品经理）"},
    {"employee_id": 4, "roles": ["manager"], "department_id": 9, "_name": "赵六（AI 组长）"},
    {"employee_id": 6, "roles": ["talent_dev"], "department_id": 4, "_name": "孙八（HRBP/人才发展）"},
]


def _inject_mock_employee(run_context: RunContext) -> None:
    """无登录态时基于 session_id 确定性选择一个模拟员工，同一会话始终同一人。"""
    seed = hash(run_context.session_id or "") % len(_MOCK_EMPLOYEES)
    mock = _MOCK_EMPLOYEES[seed]
    state = run_context.session_state
    if state is None:
        run_context.session_state = {}
        state = run_context.session_state
    state["employee_id"] = mock["employee_id"]
    state["roles"] = mock["roles"]
    state["department_id"] = mock["department_id"]
    logger.info("注入模拟员工登录态: {name} (id={eid})", name=mock["_name"], eid=mock["employee_id"])


def get_employee_id(run_context: RunContext) -> int:
    """从 session_state 提取 employee_id。

    仅在 DEBUG 或 ALLOW_MOCK_IDENTITY=true 时允许注入模拟员工。

    Returns:
        员工 ID
    """
    state = run_context.session_state
    if not state or "employee_id" not in state:
        if not settings.DEBUG and not settings.ALLOW_MOCK_IDENTITY:
            raise ValueError("未检测到登录态，请先完成认证")
        _inject_mock_employee(run_context)
        state = run_context.session_state
    logger.info(
        "当前用户: employee_id={eid}, roles={roles}, department_id={dept}",
        eid=state["employee_id"],  # type: ignore[index]
        roles=state.get("roles", []),  # type: ignore[union-attr]
        dept=state.get("department_id"),  # type: ignore[union-attr]
    )
    return state["employee_id"]  # type: ignore[index]


def get_manager_info(run_context: RunContext) -> tuple[int, int]:
    """从 session_state 提取主管信息。

    注：权限校验已通过动态 tools 在 Agent 层实现，此函数仅负责提取身份信息。

    Returns:
        (employee_id, department_id)
    """
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    return employee_id, state["department_id"]  # type: ignore[index]


def get_admin_id(run_context: RunContext) -> int:
    """从 session_state 提取管理者身份。

    注：权限校验已通过动态 tools 在 Agent 层实现，此函数仅负责提取身份信息。

    Returns:
        员工 ID
    """
    return get_employee_id(run_context)


def get_talent_dev_id(run_context: RunContext) -> int:
    """从 session_state 提取人才发展角色身份。

    注：权限校验已通过动态 tools 在 Agent 层实现，此函数仅负责提取身份信息。

    Returns:
        员工 ID
    """
    return get_employee_id(run_context)
