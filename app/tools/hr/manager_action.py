"""主管审批 Tools — 审批请假申请、加班申请"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.manager_query import _check_manager


async def approve_leave_request(
    run_context: RunContext,
    request_id: int,
    action: str,
    comment: str = "",
) -> str:
    """审批请假申请。action 为"通过"或"拒绝"，comment 为审批备注。

    Args:
        request_id: 请假申请 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    try:
        emp_id, dept_id = _check_manager(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.approve_leave_request(
            session, emp_id, dept_id, request_id, action, comment,
        )
        return result.model_dump_json()


async def approve_overtime_request(
    run_context: RunContext,
    record_id: int,
    action: str,
    comment: str = "",
) -> str:
    """审批加班申请。action 为"通过"或"拒绝"，comment 为审批备注。

    Args:
        record_id: 加班记录 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    try:
        emp_id, dept_id = _check_manager(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.approve_overtime_request(
            session, emp_id, dept_id, record_id, action, comment,
        )
        return result.model_dump_json()
