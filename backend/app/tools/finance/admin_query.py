"""财务人员查询 Tools — 报销列表、费用汇总、预算分析、应收应付"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import finance as fin_service
from app.tools.finance.utils import get_finance_id


async def fin_admin_get_all_reimbursements(
    run_context: RunContext,
    status: str | None = None,
    type: str | None = None,
    department_id: int | None = None,
) -> str:
    """查询全部报销单，支持按状态/类型/部门筛选。

    Args:
        status: 报销单状态（pending/approved/rejected/returned/paid）
        type: 报销类型（差旅/餐费/交通/办公/招待/其他）
        department_id: 部门 ID
    """
    logger.info("tool=fin_admin_get_all_reimbursements | s={s} t={t} d={d}", s=status, t=type, d=department_id)
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_all_reimbursements(session, status, type, department_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_admin_get_expense_summary(
    run_context: RunContext, group_by: str = "department",
) -> str:
    """费用汇总报表。按维度分组（department 部门 / type 科目 / month 月度）。

    Args:
        group_by: 分组维度（department/type/month），默认 department
    """
    logger.info("tool=fin_admin_get_expense_summary | group_by={g}", g=group_by)
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_expense_summary(session, group_by)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_admin_get_budget_analysis(run_context: RunContext) -> str:
    """全公司预算执行分析：各部门当年预算总额、已用、余额、执行率。"""
    logger.info("tool=fin_admin_get_budget_analysis")
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_budget_analysis(session)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_admin_get_payables(run_context: RunContext, status: str | None = None) -> str:
    """查询应付款列表，可按状态筛选（pending/paid/overdue）。

    Args:
        status: 应付款状态
    """
    logger.info("tool=fin_admin_get_payables | status={s}", s=status)
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_payables(session, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_admin_get_receivables(run_context: RunContext, status: str | None = None) -> str:
    """查询应收款列表，可按状态筛选（pending/received/overdue）。

    Args:
        status: 应收款状态
    """
    logger.info("tool=fin_admin_get_receivables | status={s}", s=status)
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await fin_service.get_receivables(session, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
