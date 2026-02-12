"""管理者查询 Tools — 全公司数据查询、薪资社保查看、汇总报表"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.utils import get_admin_id


async def admin_get_all_employees(run_context: RunContext) -> str:
    """查询全公司员工列表（所有部门）"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        members = await hr_service.get_all_employees(session)
        return "[" + ",".join(m.model_dump_json() for m in members) + "]"


async def admin_get_employee_salary(
    run_context: RunContext,
    employee_id: int,
    year_month: str | None = None,
) -> str:
    """查询任意员工的薪资明细。year_month 格式 YYYY-MM，不传则返回最近 3 个月。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_any_employee_salary(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_employee_social_insurance(
    run_context: RunContext,
    employee_id: int,
    year_month: str | None = None,
) -> str:
    """查询任意员工的社保缴纳明细。year_month 格式 YYYY-MM，不传则返回最近 3 个月。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_any_employee_social_insurance(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_employee_profile(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询任意员工的完整档案（含基本信息、绩效、履历、薪资、社保）"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        profile = await hr_service.get_any_employee_profile(session, employee_id)
        return profile.model_dump_json()


async def admin_get_all_leave_requests(
    run_context: RunContext,
    status: str | None = None,
) -> str:
    """查询全公司请假记录。可传 status="待审批" 过滤。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_all_leave_requests(session, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_all_attendance(
    run_context: RunContext,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
) -> str:
    """查询全公司考勤记录。日期格式 YYYY-MM-DD，可传 status 过滤。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_all_attendance(session, start_date, end_date, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_all_overtime_records(
    run_context: RunContext,
    year_month: str | None = None,
    status: str | None = None,
) -> str:
    """查询全公司加班记录。year_month 格式 YYYY-MM，可传 status 过滤。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_all_overtime_records(session, year_month, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


# ── 汇总报表 ─────────────────────────────────────────────────


async def admin_get_department_headcount(run_context: RunContext) -> str:
    """各部门人员统计（在职、试用期人数）"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_department_headcount(session)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_attendance_summary(
    run_context: RunContext,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """全公司考勤汇总（正常/迟到/早退/缺卡/外勤人次）。日期格式 YYYY-MM-DD。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.get_attendance_summary(session, start_date, end_date)
        return result.model_dump_json()


async def admin_get_salary_summary(
    run_context: RunContext,
    year_month: str | None = None,
) -> str:
    """各部门薪资汇总（员工数、薪资总额、平均薪资）。year_month 格式 YYYY-MM。"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_salary_summary(session, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def admin_get_leave_summary(run_context: RunContext) -> str:
    """假期使用与待审批汇总（各假期类型已用天数、待审批数量）"""
    try:
        get_admin_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_leave_summary(session)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
