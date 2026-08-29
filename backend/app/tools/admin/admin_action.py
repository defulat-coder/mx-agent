"""行政管理员操作 Tools — 会议室管理、申领审批、快递登记"""

import json

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException
from app.services import admin as admin_service
from app.tools.admin.utils import get_admin_staff_id


def _error_result(code: int, message: str) -> str:
    return json.dumps({"status": "error", "code": code, "message": message}, ensure_ascii=False)


async def adm_admin_release_room(
    run_context: RunContext,
    room_id: int,
    status: str,
) -> str:
    """设置会议室状态（available 恢复使用 / maintenance 维护中）。

    Args:
        room_id: 会议室 ID
        status: 目标状态（available/maintenance）
    """
    logger.info("tool=adm_admin_release_room | room_id={r} status={s}", r=room_id, s=status)
    try:
        get_admin_staff_id(run_context)
        async with async_session_factory() as session, session.begin():
            record = await admin_service.release_room(session, room_id, status)
        return record.model_dump_json()
    except AppException as exc:
        return _error_result(exc.code, exc.message)
    except ValueError as exc:
        return _error_result(ErrorCode.FORBIDDEN, str(exc))
    except Exception:
        logger.exception("设置会议室状态失败")
        return _error_result(ErrorCode.INTERNAL_ERROR, "服务内部错误")


async def adm_admin_approve_supply(
    run_context: RunContext,
    request_id: int,
    action: str,
    remark: str = "",
) -> str:
    """审批办公用品申领单：approve 通过（自动扣减库存）/ reject 驳回。

    Args:
        request_id: 申领单 ID
        action: 操作（approve/reject）
        remark: 审批备注
    """
    logger.info("tool=adm_admin_approve_supply | request_id={r} action={a}", r=request_id, a=action)
    try:
        admin_id = get_admin_staff_id(run_context)
        async with async_session_factory() as session, session.begin():
            record = await admin_service.approve_supply(session, request_id, admin_id, action, remark)
        return record.model_dump_json()
    except AppException as exc:
        return _error_result(exc.code, exc.message)
    except ValueError as exc:
        return _error_result(ErrorCode.FORBIDDEN, str(exc))
    except Exception:
        logger.exception("审批办公用品申领单失败")
        return _error_result(ErrorCode.INTERNAL_ERROR, "服务内部错误")


async def adm_admin_register_express(
    run_context: RunContext,
    tracking_no: str,
    type: str,
    employee_id: int,
    courier: str,
    remark: str = "",
) -> str:
    """登记快递收发记录。

    Args:
        tracking_no: 快递单号
        type: 类型（receive 收件 / send 寄件）
        employee_id: 员工 ID
        courier: 快递公司（顺丰/中通/圆通/韵达/京东等）
        remark: 备注
    """
    logger.info("tool=adm_admin_register_express | tracking_no={tn}", tn=tracking_no)
    try:
        get_admin_staff_id(run_context)
        async with async_session_factory() as session, session.begin():
            record = await admin_service.register_express(session, tracking_no, type, employee_id, courier, remark)
        return record.model_dump_json()
    except AppException as exc:
        return _error_result(exc.code, exc.message)
    except ValueError as exc:
        return _error_result(ErrorCode.FORBIDDEN, str(exc))
    except Exception:
        logger.exception("登记快递失败")
        return _error_result(ErrorCode.INTERNAL_ERROR, "服务内部错误")
