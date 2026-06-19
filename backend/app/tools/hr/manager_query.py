"""主管团队查询 Tools — 团队成员、考勤、请假、假期余额、加班、员工档案"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.utils import get_manager_info
from loguru import logger


async def get_team_members(run_context: RunContext) -> str:
    """查询团队成员列表（管辖部门递归子部门内所有员工的基本信息）"""
    logger.info("tool=get_team_members")
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        members = await hr_service.get_team_members(session, emp_id, dept_id)
        return "[" + ",".join(m.model_dump_json() for m in members) + "]"


async def get_team_attendance(
    run_context: RunContext,
    employee_id: int | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """查询团队考勤记录。可指定 employee_id 查单人，或传 status="异常" 查全员异常。日期格式 YYYY-MM-DD。"""
    logger.info("tool=get_team_attendance | employee_id={employee_id} status={status} start_date={start_date} end_date={end_date}", employee_id=employee_id, status=status, start_date=start_date, end_date=end_date)
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_team_attendance(
            session, emp_id, dept_id, employee_id, status, start_date, end_date,
        )
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_team_leave_requests(
    run_context: RunContext,
    status: str | None = None,
) -> str:
    """查询团队请假记录。可传 status="待审批" 过滤，不传则返回当年全部。"""
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_team_leave_requests(session, emp_id, dept_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_team_leave_balances(
    run_context: RunContext,
    employee_id: int | None = None,
) -> str:
    """查询团队假期余额。可指定 employee_id 查单人，不传则查全员。"""
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_team_leave_balances(session, emp_id, dept_id, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_team_overtime_records(
    run_context: RunContext,
    year_month: str | None = None,
    status: str | None = None,
) -> str:
    """查询团队加班记录。year_month 格式 YYYY-MM，可传 status="待审批" 过滤。"""
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_team_overtime_records(
            session, emp_id, dept_id, year_month, status,
        )
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def get_employee_profile(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询指定员工的完整档案（基本信息 + 绩效考评历史 + 在职履历），不含薪资和社保。"""
    logger.info("tool=get_employee_profile | employee_id={employee_id}", employee_id=employee_id)
    try:
        emp_id, dept_id = get_manager_info(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        profile = await hr_service.get_employee_profile(session, emp_id, dept_id, employee_id)
        return profile.model_dump_json()
