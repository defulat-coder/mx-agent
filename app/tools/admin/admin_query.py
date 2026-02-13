"""行政管理员查询 Tools — 预订、申领单、库存、快递、访客、统计"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import admin as admin_service
from app.tools.admin.utils import get_admin_staff_id


async def adm_admin_get_all_bookings(
    run_context: RunContext,
    room_id: int | None = None,
    status: str | None = None,
    date: str | None = None,
) -> str:
    """查询全部会议室预订记录，支持按会议室/状态/日期筛选。

    Args:
        room_id: 会议室 ID
        status: 预订状态（active/cancelled/completed）
        date: 日期（YYYY-MM-DD）
    """
    logger.info("tool=adm_admin_get_all_bookings | room={r} status={s} date={d}", r=room_id, s=status, d=date)
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await admin_service.get_all_bookings(session, room_id, status, date)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_admin_get_supply_requests(run_context: RunContext, status: str | None = None) -> str:
    """查询全部办公用品申领单，可按状态筛选（pending/approved/rejected）。

    Args:
        status: 申领单状态
    """
    logger.info("tool=adm_admin_get_supply_requests | status={s}", s=status)
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await admin_service.get_supply_requests(session, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_admin_get_supply_stock(run_context: RunContext, category: str | None = None) -> str:
    """查询办公用品库存，可按分类筛选（文具/耗材/清洁/其他）。

    Args:
        category: 用品分类
    """
    logger.info("tool=adm_admin_get_supply_stock | category={c}", c=category)
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await admin_service.get_supply_stock(session, category)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_admin_get_all_express(
    run_context: RunContext, status: str | None = None, type: str | None = None,
) -> str:
    """查询全部快递记录，可按状态/类型筛选。

    Args:
        status: 快递状态（pending/picked_up/sent）
        type: 快递类型（receive/send）
    """
    logger.info("tool=adm_admin_get_all_express | status={s} type={t}", s=status, t=type)
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await admin_service.get_all_express(session, status, type)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_admin_get_visitors(
    run_context: RunContext, date: str | None = None, status: str | None = None,
) -> str:
    """查询全部访客预约记录，可按日期/状态筛选。

    Args:
        date: 来访日期（YYYY-MM-DD）
        status: 状态（pending/checked_in/checked_out/cancelled）
    """
    logger.info("tool=adm_admin_get_visitors | date={d} status={s}", d=date, s=status)
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await admin_service.get_all_visitors(session, date, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def adm_admin_usage_stats(run_context: RunContext) -> str:
    """行政综合统计：会议室使用率、办公用品消耗等。"""
    logger.info("tool=adm_admin_usage_stats")
    try:
        get_admin_staff_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        room_stats = await admin_service.room_usage_stats(session)
        supply_stats = await admin_service.supply_stats(session)
        import json
        result = {
            "room_usage": json.loads(room_stats.model_dump_json()),
            "supply_stats": json.loads(supply_stats.model_dump_json()),
        }
        return json.dumps(result, ensure_ascii=False)
