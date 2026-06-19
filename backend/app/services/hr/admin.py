"""Admin-scoped HR queries, reports, and approvals."""

from datetime import date, datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.hr import (
    AttendanceRecord,
    Department,
    Employee,
    EmploymentHistory,
    LeaveRequest,
    OvertimeRecord,
    PerformanceReview,
    SalaryRecord,
    SocialInsuranceRecord,
)
from app.schemas.hr import (
    ApprovalResponse,
    AttendanceSummaryResponse,
    DepartmentHeadcountResponse,
    EmployeeFullProfileResponse,
    EmploymentHistoryResponse,
    LeaveSummaryResponse,
    PerformanceReviewResponse,
    SalaryRecordResponse,
    SalarySummaryResponse,
    SocialInsuranceResponse,
    TeamAttendanceResponse,
    TeamLeaveRequestResponse,
    TeamMemberResponse,
    TeamOvertimeRecordResponse,
)
from app.services.hr.employee import (
    get_employee_info,
    get_salary_records,
    get_social_insurance,
)
from app.services.hr.manager import _get_dept_name_map, _get_employee_name_map


# ── 管理者 Service ───────────────────────────────────────────


async def get_all_employees(session: AsyncSession) -> list[TeamMemberResponse]:
    """查询全公司员工列表。"""
    stmt = select(Employee).order_by(Employee.id)
    employees = (await session.execute(stmt)).scalars().all()
    dept_ids = list({e.department_id for e in employees if e.department_id})
    dept_map = await _get_dept_name_map(session, dept_ids)
    return [
        TeamMemberResponse(
            employee_id=e.id, name=e.name, employee_no=e.employee_no,
            department=dept_map.get(e.department_id) if e.department_id else None,
            position=e.position, level=e.level, status=e.status,
        )
        for e in employees
    ]


async def get_any_employee_salary(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[SalaryRecordResponse]:
    """查询任意员工的薪资明细（管理者专用）。"""
    logger.info("管理者查询薪资 | target_employee_id={eid} year_month={ym}", eid=employee_id, ym=year_month or "最近3月")
    return await get_salary_records(session, employee_id, year_month)


async def get_any_employee_social_insurance(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[SocialInsuranceResponse]:
    """查询任意员工的社保明细（管理者专用）。"""
    logger.info("管理者查询社保 | target_employee_id={eid} year_month={ym}", eid=employee_id, ym=year_month or "最近3月")
    return await get_social_insurance(session, employee_id, year_month)


async def get_any_employee_profile(
    session: AsyncSession, target_employee_id: int,
) -> EmployeeFullProfileResponse:
    """查询任意员工的完整档案（含薪资社保，管理者专用）。

    Raises:
        NotFoundException: 员工不存在
    """
    logger.info("查询完整档案 | target_employee_id={eid}", eid=target_employee_id)
    info = await get_employee_info(session, target_employee_id)

    perf_rows = (await session.execute(
        select(PerformanceReview)
        .where(PerformanceReview.employee_id == target_employee_id)
        .order_by(PerformanceReview.year.desc(), PerformanceReview.half.desc())
    )).scalars().all()

    hist_rows = (await session.execute(
        select(EmploymentHistory)
        .where(EmploymentHistory.employee_id == target_employee_id)
        .order_by(EmploymentHistory.start_date.desc())
    )).scalars().all()

    salary_rows = (await session.execute(
        select(SalaryRecord)
        .where(SalaryRecord.employee_id == target_employee_id)
        .order_by(SalaryRecord.year_month.desc())
        .limit(6)
    )).scalars().all()

    si_rows = (await session.execute(
        select(SocialInsuranceRecord)
        .where(SocialInsuranceRecord.employee_id == target_employee_id)
        .order_by(SocialInsuranceRecord.year_month.desc())
        .limit(6)
    )).scalars().all()

    return EmployeeFullProfileResponse(
        info=info,
        performance_reviews=[
            PerformanceReviewResponse(
                year=p.year, half=p.half, rating=p.rating,
                score=p.score, reviewer=p.reviewer, comment=p.comment,
            )
            for p in perf_rows
        ],
        employment_histories=[
            EmploymentHistoryResponse(
                start_date=h.start_date, end_date=h.end_date,
                department=h.department, position=h.position, level=h.level,
                change_type=h.change_type, remark=h.remark,
            )
            for h in hist_rows
        ],
        salary_records=[
            SalaryRecordResponse(
                year_month=s.year_month, base_salary=s.base_salary, bonus=s.bonus,
                allowance=s.allowance, deduction=s.deduction,
                social_insurance=s.social_insurance, housing_fund=s.housing_fund,
                tax=s.tax, net_salary=s.net_salary,
            )
            for s in salary_rows
        ],
        social_insurance_records=[
            SocialInsuranceResponse(
                year_month=si.year_month, pension=si.pension, medical=si.medical,
                unemployment=si.unemployment, housing_fund=si.housing_fund,
                pension_company=si.pension_company, medical_company=si.medical_company,
                unemployment_company=si.unemployment_company,
                injury_company=si.injury_company, maternity_company=si.maternity_company,
                housing_fund_company=si.housing_fund_company,
            )
            for si in si_rows
        ],
    )


async def get_all_leave_requests(
    session: AsyncSession, status: str | None = None,
) -> list[TeamLeaveRequestResponse]:
    """查询全公司请假记录（管理者专用）。"""
    stmt = select(LeaveRequest)
    if status:
        stmt = stmt.where(LeaveRequest.status == status)
    else:
        current_year = date.today().year
        stmt = stmt.where(LeaveRequest.start_date >= date(current_year, 1, 1))
    stmt = stmt.order_by(LeaveRequest.start_date.desc())
    rows = (await session.execute(stmt)).scalars().all()

    emp_ids = list({r.employee_id for r in rows})
    name_map = await _get_employee_name_map(session, emp_ids)
    return [
        TeamLeaveRequestResponse(
            request_id=r.id, employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            leave_type=r.leave_type, start_date=r.start_date, end_date=r.end_date,
            days=r.days, reason=r.reason, status=r.status,
        )
        for r in rows
    ]


async def get_all_attendance(
    session: AsyncSession, start_date: str | None = None, end_date: str | None = None,
    status: str | None = None,
) -> list[TeamAttendanceResponse]:
    """查询全公司考勤记录（管理者专用）。"""
    stmt = select(AttendanceRecord)
    if start_date:
        stmt = stmt.where(AttendanceRecord.date >= date.fromisoformat(start_date))
    else:
        stmt = stmt.where(AttendanceRecord.date >= date.today().replace(day=1))
    if end_date:
        stmt = stmt.where(AttendanceRecord.date <= date.fromisoformat(end_date))
    if status:
        stmt = stmt.where(AttendanceRecord.status == status)
    stmt = stmt.order_by(AttendanceRecord.date.desc(), AttendanceRecord.employee_id)
    rows = (await session.execute(stmt)).scalars().all()

    emp_ids = list({r.employee_id for r in rows})
    name_map = await _get_employee_name_map(session, emp_ids)
    return [
        TeamAttendanceResponse(
            employee_id=r.employee_id, employee_name=name_map.get(r.employee_id, ""),
            date=r.date, check_in=r.check_in, check_out=r.check_out,
            status=r.status, remark=r.remark,
        )
        for r in rows
    ]


async def get_all_overtime_records(
    session: AsyncSession, year_month: str | None = None, status: str | None = None,
) -> list[TeamOvertimeRecordResponse]:
    """查询全公司加班记录（管理者专用）。"""
    stmt = select(OvertimeRecord)
    if year_month:
        ym_parts = year_month.split("-")
        y, m = int(ym_parts[0]), int(ym_parts[1])
        month_start = date(y, m, 1)
        next_m = m + 1 if m < 12 else 1
        next_y = y if m < 12 else y + 1
        month_end = date(next_y, next_m, 1)
        stmt = stmt.where(OvertimeRecord.date >= month_start, OvertimeRecord.date < month_end)
    else:
        stmt = stmt.where(OvertimeRecord.date >= date.today().replace(day=1))
    if status:
        stmt = stmt.where(OvertimeRecord.status == status)
    stmt = stmt.order_by(OvertimeRecord.date.desc(), OvertimeRecord.employee_id)
    rows = (await session.execute(stmt)).scalars().all()

    emp_ids = list({r.employee_id for r in rows})
    name_map = await _get_employee_name_map(session, emp_ids)
    return [
        TeamOvertimeRecordResponse(
            record_id=r.id, employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            date=r.date, start_time=r.start_time, end_time=r.end_time,
            hours=r.hours, type=r.type, status=r.status,
        )
        for r in rows
    ]


# ── 管理者汇总报表 ──────────────────────────────────────────


async def get_department_headcount(session: AsyncSession) -> list[DepartmentHeadcountResponse]:
    """各部门人员统计。"""
    depts = (await session.execute(select(Department).order_by(Department.id))).scalars().all()
    employees = (await session.execute(select(Employee))).scalars().all()

    dept_stats: dict[int, dict[str, int]] = {}
    for e in employees:
        did = e.department_id or 0
        if did not in dept_stats:
            dept_stats[did] = {"active": 0, "probation": 0}
        if e.status == "在职":
            dept_stats[did]["active"] += 1
        elif e.status == "试用期":
            dept_stats[did]["probation"] += 1

    dept_name_map = {d.id: d.name for d in depts}
    return [
        DepartmentHeadcountResponse(
            department_id=did,
            department_name=dept_name_map.get(did, "未知"),
            active_count=stats["active"],
            probation_count=stats["probation"],
            total_count=stats["active"] + stats["probation"],
        )
        for did, stats in sorted(dept_stats.items())
    ]


async def get_attendance_summary(
    session: AsyncSession, start_date: str | None = None, end_date: str | None = None,
) -> AttendanceSummaryResponse:
    """全公司考勤汇总统计。"""
    stmt = select(AttendanceRecord)
    sd = date.fromisoformat(start_date) if start_date else date.today().replace(day=1)
    ed = date.fromisoformat(end_date) if end_date else date.today()
    stmt = stmt.where(AttendanceRecord.date >= sd, AttendanceRecord.date <= ed)
    rows = (await session.execute(stmt)).scalars().all()

    counts = {"正常": 0, "迟到": 0, "早退": 0, "缺卡": 0, "外勤": 0}
    for r in rows:
        if r.status in counts:
            counts[r.status] += 1

    return AttendanceSummaryResponse(
        normal_count=counts["正常"], late_count=counts["迟到"],
        early_leave_count=counts["早退"], absent_count=counts["缺卡"],
        outside_count=counts["外勤"], start_date=sd, end_date=ed,
    )


async def get_salary_summary(
    session: AsyncSession, year_month: str | None = None,
) -> list[SalarySummaryResponse]:
    """各部门薪资汇总。"""
    ym = year_month or datetime.now().strftime("%Y-%m")
    stmt = select(SalaryRecord).where(SalaryRecord.year_month == ym)
    rows = (await session.execute(stmt)).scalars().all()

    emp_ids = list({r.employee_id for r in rows})
    if not emp_ids:
        return []
    emp_dept = {}
    emp_rows = (await session.execute(
        select(Employee.id, Employee.department_id).where(Employee.id.in_(emp_ids))
    )).fetchall()
    for eid, did in emp_rows:
        emp_dept[eid] = did

    dept_stats: dict[int, dict] = {}
    for r in rows:
        did = emp_dept.get(r.employee_id, 0)
        if did not in dept_stats:
            dept_stats[did] = {"count": 0, "total": 0}
        dept_stats[did]["count"] += 1
        dept_stats[did]["total"] += float(r.net_salary)

    dept_ids = list(dept_stats.keys())
    dept_name_map = await _get_dept_name_map(session, dept_ids)
    return [
        SalarySummaryResponse(
            department_id=did,
            department_name=dept_name_map.get(did, "未知"),
            employee_count=stats["count"],
            total_net_salary=round(stats["total"], 2),
            avg_net_salary=round(stats["total"] / stats["count"], 2) if stats["count"] else 0,
        )
        for did, stats in sorted(dept_stats.items())
    ]


async def get_leave_summary(session: AsyncSession) -> list[LeaveSummaryResponse]:
    """假期使用与待审批汇总。"""
    current_year = date.today().year

    # 已使用天数（已通过的）
    approved_stmt = (
        select(LeaveRequest)
        .where(LeaveRequest.start_date >= date(current_year, 1, 1))
        .where(LeaveRequest.status == "已通过")
    )
    approved = (await session.execute(approved_stmt)).scalars().all()

    # 待审批数量
    pending_stmt = (
        select(LeaveRequest)
        .where(LeaveRequest.start_date >= date(current_year, 1, 1))
        .where(LeaveRequest.status == "待审批")
    )
    pending = (await session.execute(pending_stmt)).scalars().all()

    type_stats: dict[str, dict] = {}
    for r in approved:
        if r.leave_type not in type_stats:
            type_stats[r.leave_type] = {"used": 0, "pending": 0}
        type_stats[r.leave_type]["used"] += float(r.days)
    for r in pending:
        if r.leave_type not in type_stats:
            type_stats[r.leave_type] = {"used": 0, "pending": 0}
        type_stats[r.leave_type]["pending"] += 1

    return [
        LeaveSummaryResponse(
            leave_type=lt,
            total_days_used=round(stats["used"], 1),
            pending_count=stats["pending"],
        )
        for lt, stats in sorted(type_stats.items())
    ]


async def admin_approve_leave_request(
    session: AsyncSession, request_id: int, action: str, comment: str = "",
) -> ApprovalResponse:
    """管理者审批请假申请（全公司范围，无部门限制）。"""
    logger.info("管理者审批请假 | request_id={rid} action={act}", rid=request_id, act=action)
    leave_req = (await session.execute(
        select(LeaveRequest).where(LeaveRequest.id == request_id)
    )).scalar_one_or_none()
    if not leave_req:
        raise NotFoundException(message="请假申请不存在")
    if leave_req.status != "待审批":
        return ApprovalResponse(
            success=False,
            message=f"该申请当前状态为「{leave_req.status}」，无法审批",
        )
    new_status = "已通过" if action == "通过" else "已拒绝"
    leave_req.status = new_status
    await session.commit()
    return ApprovalResponse(success=True, request_id=request_id, action=action, message=f"请假申请已{action}")


async def admin_approve_overtime_request(
    session: AsyncSession, record_id: int, action: str, comment: str = "",
) -> ApprovalResponse:
    """管理者审批加班申请（全公司范围，无部门限制）。"""
    logger.info("管理者审批加班 | record_id={rid} action={act}", rid=record_id, act=action)
    ot_record = (await session.execute(
        select(OvertimeRecord).where(OvertimeRecord.id == record_id)
    )).scalar_one_or_none()
    if not ot_record:
        raise NotFoundException(message="加班记录不存在")
    if ot_record.status != "待审批":
        return ApprovalResponse(
            success=False,
            message=f"该记录当前状态为「{ot_record.status}」，无法审批",
        )
    new_status = "已通过" if action == "通过" else "已拒绝"
    ot_record.status = new_status
    await session.commit()
    return ApprovalResponse(success=True, request_id=record_id, action=action, message=f"加班申请已{action}")
