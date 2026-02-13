"""财务员工查询 Tools — 报销查询、预算查询、个税查询"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import finance as fin_service
from app.tools.hr.utils import get_employee_id


async def fin_get_my_reimbursements(run_context: RunContext, status: str | None = None) -> str:
    """查询我的报销单列表。可选按状态筛选（pending/approved/rejected/returned/paid）。

    Args:
        status: 报销单状态筛选，不传则返回全部
    """
    logger.info("tool=fin_get_my_reimbursements | status={s}", s=status)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await fin_service.get_my_reimbursements(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def fin_get_reimbursement_detail(run_context: RunContext, reimbursement_id: int) -> str:
    """查询报销单详情（含明细行、审核信息）。

    Args:
        reimbursement_id: 报销单 ID
    """
    logger.info("tool=fin_get_reimbursement_detail | id={rid}", rid=reimbursement_id)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        try:
            record = await fin_service.get_reimbursement_detail(session, reimbursement_id, employee_id)
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def fin_get_department_budget(run_context: RunContext, year: int | None = None) -> str:
    """查询所在部门当年预算余额。

    Args:
        year: 年度，不传默认当年
    """
    logger.info("tool=fin_get_department_budget | year={y}", y=year)
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    department_id = state.get("department_id")  # type: ignore[union-attr]
    if not department_id:
        return "无法获取部门信息"
    async with async_session_factory() as session:
        record = await fin_service.get_department_budget(session, department_id, year)
        if not record:
            return "未找到该部门的预算数据"
        return record.model_dump_json()


async def fin_get_my_tax(run_context: RunContext, year_month: str | None = None) -> str:
    """查询个人所得税明细。不传月份默认返回近 3 个月。

    Args:
        year_month: 月份（YYYY-MM），不传返回近 3 个月
    """
    logger.info("tool=fin_get_my_tax | year_month={ym}", ym=year_month)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await fin_service.get_my_tax(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
