"""财务主管查询 Tools — 部门预算总览、费用明细、预算预警"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import finance as fin_service
from app.tools.hr.utils import get_manager_info


async def fin_mgr_get_budget_overview(run_context: RunContext) -> str:
    """查看本部门预算总览（总额/已用/余额/执行率）。需主管角色。"""
    logger.info("tool=fin_mgr_get_budget_overview")
    try:
        _, department_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_budget_overview(session, department_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_mgr_get_expense_detail(
    run_context: RunContext,
    category: str | None = None,
    year_month: str | None = None,
) -> str:
    """查看本部门费用明细。可按科目、月份筛选。需主管角色。

    Args:
        category: 费用科目（差旅/餐费/交通/办公/招待/其他）
        year_month: 月份（YYYY-MM）
    """
    logger.info("tool=fin_mgr_get_expense_detail | cat={c} ym={y}", c=category, y=year_month)
    try:
        _, department_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_expense_detail(session, department_id, category, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_mgr_get_budget_alert(run_context: RunContext) -> str:
    """查看本部门预算预警（执行率超 80% 的预算）。需主管角色。"""
    logger.info("tool=fin_mgr_get_budget_alert")
    try:
        _, department_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_budget_alert(session, department_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
