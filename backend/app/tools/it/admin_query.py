"""IT 管理员查询 Tools — 工单列表、设备列表、统计报表"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import it as it_service
from app.tools.it.utils import get_it_admin_id


async def it_admin_get_tickets(
    run_context: RunContext,
    status: str | None = None,
    type: str | None = None,
    priority: str | None = None,
) -> str:
    """查询全部 IT 工单，支持按状态/类型/优先级筛选。

    Args:
        status: 工单状态（open/in_progress/resolved/closed）
        type: 工单类型（repair/password_reset/software_install/permission/other）
        priority: 优先级（low/medium/high/urgent）
    """
    logger.info("tool=it_admin_get_tickets | status={s} type={t} priority={p}", s=status, t=type, p=priority)
    try:
        get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await it_service.get_all_tickets(session, status, type, priority)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def it_admin_get_assets(
    run_context: RunContext,
    status: str | None = None,
    type: str | None = None,
) -> str:
    """查询全部 IT 设备资产，支持按状态/类型筛选。

    Args:
        status: 设备状态（idle/in_use/maintenance/scrapped）
        type: 设备类型（laptop/desktop/monitor/peripheral/other）
    """
    logger.info("tool=it_admin_get_assets | status={s} type={t}", s=status, t=type)
    try:
        get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await it_service.get_all_assets(session, status, type)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def it_admin_ticket_stats(run_context: RunContext) -> str:
    """IT 工单统计：各状态/类型/优先级数量、平均处理时长。"""
    logger.info("tool=it_admin_ticket_stats")
    try:
        get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        stats = await it_service.ticket_stats(session)
        return stats.model_dump_json()


async def it_admin_asset_stats(run_context: RunContext) -> str:
    """IT 设备统计：各状态/类型数量、各部门设备分配。"""
    logger.info("tool=it_admin_asset_stats")
    try:
        get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        stats = await it_service.asset_stats(session)
        return stats.model_dump_json()


async def it_admin_fault_trend(run_context: RunContext, months: int = 3) -> str:
    """IT 故障趋势分析：近 N 个月各类型工单趋势、高频故障部门 TOP5。

    Args:
        months: 分析近几个月的数据，默认 3 个月
    """
    logger.info("tool=it_admin_fault_trend | months={months}", months=months)
    try:
        get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        trend = await it_service.fault_trend(session, months)
        return trend.model_dump_json()
