"""IT 员工查询 Tools — 工单查询、设备查询"""

import json

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import it as it_service
from app.tools.hr.utils import get_employee_id


async def it_get_my_tickets(run_context: RunContext, status: str | None = None) -> str:
    """查询我提交的 IT 工单列表。可选按状态筛选（open/in_progress/resolved/closed）。

    Args:
        status: 工单状态筛选，不传则返回全部
    """
    logger.info("tool=it_get_my_tickets | status={status}", status=status)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await it_service.get_my_tickets(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def it_get_ticket_detail(run_context: RunContext, ticket_id: int) -> str:
    """查询工单详情（含问题描述、处理结果等完整信息）。

    Args:
        ticket_id: 工单 ID
    """
    logger.info("tool=it_get_ticket_detail | ticket_id={ticket_id}", ticket_id=ticket_id)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        try:
            record = await it_service.get_ticket_detail(session, ticket_id, employee_id)
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def it_get_my_assets(run_context: RunContext) -> str:
    """查询我名下的 IT 设备（电脑、显示器等）。"""
    logger.info("tool=it_get_my_assets")
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await it_service.get_my_assets(session, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
