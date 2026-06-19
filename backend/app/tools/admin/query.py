"""行政员工查询 Tools — 会议室、预订、快递、访客"""

from datetime import datetime

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import admin as admin_service
from app.tools.hr.utils import get_employee_id


async def adm_get_available_rooms(
    run_context: RunContext,
    start_time: str | None = None,
    end_time: str | None = None,
) -> str:
    """查询可用会议室。可选传入时间段筛选无冲突的会议室。

    Args:
        start_time: 开始时间（ISO 格式，如 2026-02-14T09:00:00），可选
        end_time: 结束时间（ISO 格式，如 2026-02-14T10:00:00），可选
    """
    logger.info("tool=adm_get_available_rooms | start={s} end={e}", s=start_time, e=end_time)
    st = datetime.fromisoformat(start_time) if start_time else None
    et = datetime.fromisoformat(end_time) if end_time else None
    async with async_session_factory() as session:
        records = await admin_service.get_available_rooms(session, st, et)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_get_my_bookings(run_context: RunContext, status: str | None = None) -> str:
    """查询我的会议室预订记录。可选按状态筛选（active/cancelled/completed）。

    Args:
        status: 预订状态筛选，不传则返回全部
    """
    logger.info("tool=adm_get_my_bookings | status={s}", s=status)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await admin_service.get_my_bookings(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_get_my_express(run_context: RunContext, type: str | None = None) -> str:
    """查询我的快递收发记录。可选按类型筛选（receive/send）。

    Args:
        type: 快递类型筛选，不传则返回全部
    """
    logger.info("tool=adm_get_my_express | type={t}", t=type)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await admin_service.get_my_express(session, employee_id, type)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_get_my_visitors(run_context: RunContext, status: str | None = None) -> str:
    """查询我预约的访客记录。可选按状态筛选（pending/checked_in/checked_out/cancelled）。

    Args:
        status: 访客状态筛选，不传则返回全部
    """
    logger.info("tool=adm_get_my_visitors | status={s}", s=status)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await admin_service.get_my_visitors(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
