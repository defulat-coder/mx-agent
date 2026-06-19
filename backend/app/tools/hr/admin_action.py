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
    """审批请假申请（全公司范围）。action 为"通过"或"拒绝"，comment 为审批备注。

    Args:
        request_id: 请假申请 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    logger.info("tool=admin_approve_leave_request | request_id={request_id} action={action}", request_id=request_id, action=action)
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.admin_approve_leave_request(
            session, request_id, action, comment,
        )
        return result.model_dump_json()


async def admin_approve_overtime_request(
    run_context: RunContext,
    record_id: int,
    action: str,
    comment: str = "",
) -> str:
    """审批加班申请（全公司范围）。action 为"通过"或"拒绝"，comment 为审批备注。

    Args:
        record_id: 加班记录 ID
        action: 通过/拒绝
        comment: 审批备注
    """
    logger.info("tool=admin_approve_overtime_request | record_id={record_id} action={action}", record_id=record_id, action=action)
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.admin_approve_overtime_request(
            session, record_id, action, comment,
        )
        return result.model_dump_json()
