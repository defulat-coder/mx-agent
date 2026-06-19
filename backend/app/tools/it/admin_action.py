"""IT 管理员操作 Tools — 工单处理、设备分配/回收"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import it as it_service
from app.tools.it.utils import get_it_admin_id


async def it_admin_handle_ticket(
    run_context: RunContext,
    ticket_id: int,
    action: str,
    resolution: str = "",
) -> str:
    """处理 IT 工单：受理(accept)、解决(resolve)、关闭(close)。

    Args:
        ticket_id: 工单 ID
        action: 操作（accept/resolve/close）
        resolution: 处理结果说明（resolve 时填写）
    """
    logger.info("tool=it_admin_handle_ticket | ticket_id={tid} action={act}", tid=ticket_id, act=action)
    try:
        admin_id = get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            record = await it_service.handle_ticket(session, ticket_id, admin_id, action, resolution)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def it_admin_assign_asset(
    run_context: RunContext,
    asset_id: int,
    employee_id: int,
) -> str:
    """将空闲设备分配给指定员工。

    Args:
        asset_id: 设备 ID
        employee_id: 接收设备的员工 ID
    """
    logger.info("tool=it_admin_assign_asset | asset_id={aid} employee_id={eid}", aid=asset_id, eid=employee_id)
    try:
        admin_id = get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            record = await it_service.assign_asset(session, asset_id, employee_id, admin_id)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def it_admin_reclaim_asset(
    run_context: RunContext,
    asset_id: int,
) -> str:
    """从员工回收设备（设备状态变为空闲）。

    Args:
        asset_id: 设备 ID
    """
    logger.info("tool=it_admin_reclaim_asset | asset_id={aid}", aid=asset_id)
    try:
        admin_id = get_it_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            record = await it_service.reclaim_asset(session, asset_id, admin_id)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)
