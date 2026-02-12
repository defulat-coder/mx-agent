"""HR 数据查询 Tools — 封装员工薪资、考勤等只读查询，通过 RunContext 获取 employee_id"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.utils import get_employee_id


async def get_employee_info(run_context: RunContext) -> str:
    """查询当前员工的基本信息（姓名、工号、部门、岗位、职级、入职日期、状态）"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        info = await hr_service.get_employee_info(session, employee_id)
        return info.model_dump_json()


async def get_salary_records(run_context: RunContext, year_month: str | None = None) -> str:
    """查询当前员工的薪资明细。year_month 格式 YYYY-MM，不传则返回最近 3 个月。"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_salary_records(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_social_insurance(run_context: RunContext, year_month: str | None = None) -> str:
    """查询当前员工的社保公积金缴纳明细。year_month 格式 YYYY-MM，不传则返回最近 1 个月。"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_social_insurance(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_attendance(
    run_context: RunContext, start_date: str | None = None, end_date: str | None = None,
) -> str:
    """查询当前员工的考勤记录。日期格式 YYYY-MM-DD，不传则返回当月至今。"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_attendance(session, employee_id, start_date, end_date)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_leave_balance(run_context: RunContext) -> str:
    """查询当前员工的各类假期余额（年假、调休、病假等）"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_leave_balance(session, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_leave_requests(run_context: RunContext, year: int | None = None) -> str:
    """查询当前员工的请假申请记录。year 为年度，不传则当前年。"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_leave_requests(session, employee_id, year)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_overtime_records(run_context: RunContext, year_month: str | None = None) -> str:
    """查询当前员工的加班记录。year_month 格式 YYYY-MM，不传则返回当月。"""
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await hr_service.get_overtime_records(session, employee_id, year_month)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
