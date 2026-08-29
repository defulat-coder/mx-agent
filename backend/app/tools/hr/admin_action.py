"""管理者审批 Tools — 全公司范围审批请假、加班"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.utils import get_admin_id
from loguru import logger


async def admin_approve_leave_request(
    run_context: RunContext,
    request_id: int,
    action: str,
    comment: str = "",
) -> str:
    """审批请假申请（全公司范围）。comment 当前不会持久化，返回结果会明确提示。

    Args:
        request_id: 请假申请 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    logger.info("tool=admin_approve_leave_request | request_id={request_id} action={action}", request_id=request_id, action=action)
    try:
        admin_employee_id = get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        async with session.begin():
            result = await hr_service.admin_approve_leave_request(
                session, admin_employee_id, request_id, action, comment,
            )
        return result.model_dump_json()


async def admin_approve_overtime_request(
    run_context: RunContext,
    record_id: int,
    action: str,
    comment: str = "",
) -> str:
    """审批加班申请（全公司范围）。comment 当前不会持久化，返回结果会明确提示。

    Args:
        record_id: 加班记录 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    logger.info("tool=admin_approve_overtime_request | record_id={record_id} action={action}", record_id=record_id, action=action)
    try:
        admin_employee_id = get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        async with session.begin():
            result = await hr_service.admin_approve_overtime_request(
                session, admin_employee_id, record_id, action, comment,
            )
        return result.model_dump_json()
