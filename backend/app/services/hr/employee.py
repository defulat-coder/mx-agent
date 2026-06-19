"""Employee self-service HR queries."""

from datetime import date, datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.hr import (
    AttendanceRecord,
    Department,
    Employee,
    LeaveBalance,
    LeaveRequest,
    OvertimeRecord,
    SalaryRecord,
    SocialInsuranceRecord,
)
from app.schemas.hr import (
    AttendanceResponse,
    EmployeeInfoResponse,
    LeaveBalanceResponse,
    LeaveRequestResponse,
    OvertimeRecordResponse,
    SalaryRecordResponse,
    SocialInsuranceResponse,
)


async def get_employee_info(session: AsyncSession, employee_id: int) -> EmployeeInfoResponse:
    """查询员工基本信息。"""
    stmt = select(Employee).where(Employee.id == employee_id)
    employee = (await session.execute(stmt)).scalar_one_or_none()
    if not employee:
        raise NotFoundException(message="员工不存在")

    dept_name: str | None = None
    if employee.department_id:
        dept = (await session.execute(select(Department).where(Department.id == employee.department_id))).scalar_one_or_none()
        dept_name = dept.name if dept else None

    return EmployeeInfoResponse(
        employee_id=employee.id,
        name=employee.name,
        employee_no=employee.employee_no,
        department=dept_name,
        position=employee.position,
        level=employee.level,
        hire_date=employee.hire_date,
        status=employee.status,
    )


async def get_salary_records(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[SalaryRecordResponse]:
    """查询员工薪资记录。"""
    logger.info("查询薪资记录 | employee_id={eid} year_month={ym}", eid=employee_id, ym=year_month or "最近3月")
    stmt = select(SalaryRecord).where(SalaryRecord.employee_id == employee_id)
    if year_month:
        stmt = stmt.where(SalaryRecord.year_month == year_month)
    stmt = stmt.order_by(SalaryRecord.year_month.desc()).limit(3 if not year_month else 100)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        SalaryRecordResponse(
            year_month=r.year_month,
            base_salary=r.base_salary,
            bonus=r.bonus,
            allowance=r.allowance,
            deduction=r.deduction,
            social_insurance=r.social_insurance,
            housing_fund=r.housing_fund,
            tax=r.tax,
            net_salary=r.net_salary,
        )
        for r in rows
    ]


async def get_social_insurance(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[SocialInsuranceResponse]:
    """查询社保公积金缴纳明细。"""
    logger.info("查询社保记录 | employee_id={eid} year_month={ym}", eid=employee_id, ym=year_month or "最近1月")
    stmt = select(SocialInsuranceRecord).where(SocialInsuranceRecord.employee_id == employee_id)
    if year_month:
        stmt = stmt.where(SocialInsuranceRecord.year_month == year_month)
    stmt = stmt.order_by(SocialInsuranceRecord.year_month.desc()).limit(1 if not year_month else 100)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        SocialInsuranceResponse(
            year_month=r.year_month,
            pension=r.pension,
            medical=r.medical,
            unemployment=r.unemployment,
            housing_fund=r.housing_fund,
            pension_company=r.pension_company,
            medical_company=r.medical_company,
            unemployment_company=r.unemployment_company,
            injury_company=r.injury_company,
            maternity_company=r.maternity_company,
            housing_fund_company=r.housing_fund_company,
        )
        for r in rows
    ]


async def get_attendance(
    session: AsyncSession,
    employee_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[AttendanceResponse]:
    """查询考勤记录。"""
    stmt = select(AttendanceRecord).where(AttendanceRecord.employee_id == employee_id)
    if start_date:
        stmt = stmt.where(AttendanceRecord.date >= date.fromisoformat(start_date))
    else:
        first_of_month = date.today().replace(day=1)
        stmt = stmt.where(AttendanceRecord.date >= first_of_month)
    if end_date:
        stmt = stmt.where(AttendanceRecord.date <= date.fromisoformat(end_date))
    stmt = stmt.order_by(AttendanceRecord.date.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        AttendanceResponse(
            date=r.date,
            check_in=r.check_in,
            check_out=r.check_out,
            status=r.status,
            remark=r.remark,
        )
        for r in rows
    ]


async def get_leave_balance(session: AsyncSession, employee_id: int) -> list[LeaveBalanceResponse]:
    """查询当年假期余额。"""
    current_year = datetime.now().year
    stmt = (
        select(LeaveBalance)
        .where(LeaveBalance.employee_id == employee_id, LeaveBalance.year == current_year)
        .order_by(LeaveBalance.leave_type)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        LeaveBalanceResponse(
            leave_type=r.leave_type,
            total_days=r.total_days,
            used_days=r.used_days,
            remaining_days=r.remaining_days,
        )
        for r in rows
    ]


async def get_leave_requests(
    session: AsyncSession, employee_id: int, year: int | None = None,
) -> list[LeaveRequestResponse]:
    """查询请假记录。"""
    target_year = year or datetime.now().year
    year_start = date(target_year, 1, 1)
    year_end = date(target_year, 12, 31)
    stmt = (
        select(LeaveRequest)
        .where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.start_date >= year_start,
            LeaveRequest.start_date <= year_end,
        )
        .order_by(LeaveRequest.start_date.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        LeaveRequestResponse(
            leave_type=r.leave_type,
            start_date=r.start_date,
            end_date=r.end_date,
            days=r.days,
            reason=r.reason,
            status=r.status,
        )
        for r in rows
    ]


async def get_overtime_records(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[OvertimeRecordResponse]:
    """查询加班记录。"""
    stmt = select(OvertimeRecord).where(OvertimeRecord.employee_id == employee_id)
    if year_month:
        ym_parts = year_month.split("-")
        y, m = int(ym_parts[0]), int(ym_parts[1])
        month_start = date(y, m, 1)
        next_m = m + 1 if m < 12 else 1
        next_y = y if m < 12 else y + 1
        month_end = date(next_y, next_m, 1)
        stmt = stmt.where(OvertimeRecord.date >= month_start, OvertimeRecord.date < month_end)
    else:
        first_of_month = date.today().replace(day=1)
        stmt = stmt.where(OvertimeRecord.date >= first_of_month)
    stmt = stmt.order_by(OvertimeRecord.date.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        OvertimeRecordResponse(
            date=r.date,
            start_time=r.start_time,
            end_time=r.end_time,
            hours=r.hours,
            type=r.type,
            status=r.status,
        )
        for r in rows
    ]
