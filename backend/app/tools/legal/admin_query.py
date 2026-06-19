"""法务人员查询 Tools — 合同台账、到期预警、统计报表"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import legal as legal_service
from app.tools.legal.utils import get_legal_id


async def leg_admin_get_contracts(
    run_context: RunContext,
    type: str | None = None,
    status: str | None = None,
    department_id: int | None = None,
) -> str:
    """查询全公司合同台账。可按类型、状态、部门筛选。

    Args:
        type: 合同类型筛选
        status: 合同状态筛选
        department_id: 部门 ID 筛选
    """
    logger.info("tool=leg_admin_get_contracts | type={t} status={s} dept={d}", t=type, s=status, d=department_id)
    try:
        get_legal_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await legal_service.get_all_contracts(session, type, status, department_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def leg_admin_get_expiring(
    run_context: RunContext,
    days: int = 30,
) -> str:
    """查询即将到期的合同（默认 30 天内到期）。

    Args:
        days: 预警天数，默认 30
    """
    logger.info("tool=leg_admin_get_expiring | days={d}", d=days)
    try:
        get_legal_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await legal_service.get_expiring_contracts(session, days)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def leg_admin_get_stats(run_context: RunContext) -> str:
    """查询合同统计报表（总数/金额/状态分布/类型分布/即将到期数）。"""
    logger.info("tool=leg_admin_get_stats")
    try:
        get_legal_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        record = await legal_service.get_contract_stats(session)
        return record.model_dump_json()
