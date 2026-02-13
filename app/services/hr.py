"""HR 数据查询 Service — 封装员工薪资、考勤等只读查询，强制 employee_id 过滤"""

from datetime import date, datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.hr import (
    AttendanceRecord,
    Certificate,
    Department,
    DevelopmentPlan,
    Education,
    Employee,
    EmploymentHistory,
    LeaveBalance,
    LeaveRequest,
    OvertimeRecord,
    PerformanceReview,
    ProjectExperience,
    SalaryRecord,
    Skill,
    SocialInsuranceRecord,
    TalentReview,
    Training,
)
from app.schemas.hr import (
    ApprovalResponse,
    AttendanceResponse,
    AttendanceSummaryResponse,
    CertificateResponse,
    DepartmentHeadcountResponse,
    DevelopmentPlanResponse,
    EducationResponse,
    EmployeeFullProfileResponse,
    EmployeeInfoResponse,
    EmployeeProfileResponse,
    EmploymentHistoryResponse,
    IdpSummaryResponse,
    LeaveBalanceResponse,
    LeaveRequestResponse,
    LeaveSummaryResponse,
    NineGridDistributionResponse,
    OvertimeRecordResponse,
    PerformanceDistributionResponse,
    PerformanceReviewResponse,
    ProjectExperienceResponse,
    PromotionStatsResponse,
    SalaryRecordResponse,
    SalarySummaryResponse,
    SkillResponse,
    SocialInsuranceResponse,
    TalentReviewResponse,
    TeamAttendanceResponse,
    TeamLeaveBalanceResponse,
    TeamLeaveRequestResponse,
    TeamMemberResponse,
    TeamOvertimeRecordResponse,
    TrainingResponse,
    TrainingSummaryResponse,
    TurnoverAnalysisResponse,
)


async def get_employee_info(session: AsyncSession, employee_id: int) -> EmployeeInfoResponse:
    """查询员工基本信息。

    Args:
        session: 数据库会话
        employee_id: 员工 ID

    Returns:
        员工基本信息

    Raises:
        NotFoundException: 员工不存在
    """
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
    """查询员工薪资记录。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
        year_month: 月份 YYYY-MM，为空则返回最近 3 个月
    """
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
    """查询社保公积金缴纳明细。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
        year_month: 月份 YYYY-MM，为空则返回最近 1 个月
    """
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
    """查询考勤记录。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
        start_date: 开始日期 YYYY-MM-DD，为空则默认当月1号
        end_date: 结束日期 YYYY-MM-DD，为空则默认今天
    """
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
    """查询当年假期余额。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
    """
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
    """查询请假记录。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
        year: 年度，为空则当前年
    """
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
    """查询加班记录。

    Args:
        session: 数据库会话
        employee_id: 员工 ID
        year_month: 月份 YYYY-MM，为空则返回当月
    """
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


# ── 主管 Service ─────────────────────────────────────────────


async def get_managed_department_ids(session: AsyncSession, department_id: int) -> list[int]:
    """递归获取管辖部门 ID 列表（含自身），使用 PostgreSQL 递归 CTE。

    Args:
        session: 数据库会话
        department_id: 起始部门 ID
    """
    cte_sql = text("""
        WITH RECURSIVE dept_tree AS (
            SELECT id FROM departments WHERE id = :dept_id
            UNION ALL
            SELECT d.id FROM departments d INNER JOIN dept_tree dt ON d.parent_id = dt.id
        )
        SELECT id FROM dept_tree
    """)
    result = await session.execute(cte_sql, {"dept_id": department_id})
    return [row[0] for row in result.fetchall()]


async def get_managed_employee_ids(
    session: AsyncSession, manager_employee_id: int, department_id: int,
) -> list[int]:
    """获取管辖范围内所有员工 ID，含权限校验。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID

    Raises:
        ForbiddenException: 非该部门主管
    """
    dept = (await session.execute(
        select(Department).where(Department.id == department_id)
    )).scalar_one_or_none()
    if not dept or dept.manager_id != manager_employee_id:
        raise ForbiddenException(message="您不是该部门的主管，无权操作")

    dept_ids = await get_managed_department_ids(session, department_id)
    stmt = select(Employee.id).where(Employee.department_id.in_(dept_ids))
    result = await session.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def _verify_employee_in_scope(
    session: AsyncSession, employee_id: int, managed_ids: list[int],
) -> None:
    """校验目标员工是否在管辖范围内。"""
    if employee_id not in managed_ids:
        raise ForbiddenException(message="该员工不在您的管辖范围内")


async def _get_employee_name_map(session: AsyncSession, employee_ids: list[int]) -> dict[int, str]:
    """批量获取员工 ID → 姓名映射。"""
    if not employee_ids:
        return {}
    stmt = select(Employee.id, Employee.name).where(Employee.id.in_(employee_ids))
    rows = (await session.execute(stmt)).fetchall()
    return {row[0]: row[1] for row in rows}


async def _get_dept_name_map(session: AsyncSession, dept_ids: list[int]) -> dict[int, str]:
    """批量获取部门 ID → 名称映射。"""
    if not dept_ids:
        return {}
    stmt = select(Department.id, Department.name).where(Department.id.in_(dept_ids))
    rows = (await session.execute(stmt)).fetchall()
    return {row[0]: row[1] for row in rows}


async def get_team_members(
    session: AsyncSession, manager_employee_id: int, department_id: int,
) -> list[TeamMemberResponse]:
    """查询团队成员列表。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    stmt = select(Employee).where(Employee.id.in_(managed_ids)).order_by(Employee.id)
    employees = (await session.execute(stmt)).scalars().all()

    dept_ids = list({e.department_id for e in employees if e.department_id})
    dept_map = await _get_dept_name_map(session, dept_ids)

    return [
        TeamMemberResponse(
            employee_id=e.id,
            name=e.name,
            employee_no=e.employee_no,
            department=dept_map.get(e.department_id) if e.department_id else None,
            position=e.position,
            level=e.level,
            status=e.status,
        )
        for e in employees
    ]


async def get_team_attendance(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    employee_id: int | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[TeamAttendanceResponse]:
    """查询团队考勤记录。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        employee_id: 指定员工 ID，为空则查全员
        status: 考勤状态过滤，"异常"表示迟到/早退/缺卡
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    if employee_id:
        await _verify_employee_in_scope(session, employee_id, managed_ids)
        target_ids = [employee_id]
    else:
        target_ids = managed_ids

    stmt = select(AttendanceRecord).where(AttendanceRecord.employee_id.in_(target_ids))

    if start_date:
        stmt = stmt.where(AttendanceRecord.date >= date.fromisoformat(start_date))
    else:
        stmt = stmt.where(AttendanceRecord.date >= date.today().replace(day=1))
    if end_date:
        stmt = stmt.where(AttendanceRecord.date <= date.fromisoformat(end_date))

    if status == "异常":
        stmt = stmt.where(AttendanceRecord.status.in_(["迟到", "早退", "缺卡"]))
    elif status:
        stmt = stmt.where(AttendanceRecord.status == status)

    stmt = stmt.order_by(AttendanceRecord.date.desc(), AttendanceRecord.employee_id)
    rows = (await session.execute(stmt)).scalars().all()

    name_map = await _get_employee_name_map(session, target_ids)
    return [
        TeamAttendanceResponse(
            employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            date=r.date,
            check_in=r.check_in,
            check_out=r.check_out,
            status=r.status,
            remark=r.remark,
        )
        for r in rows
    ]


async def get_team_leave_requests(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    status: str | None = None,
) -> list[TeamLeaveRequestResponse]:
    """查询团队请假记录。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        status: 状态过滤（待审批/已通过/已拒绝/已撤销）
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    stmt = select(LeaveRequest).where(LeaveRequest.employee_id.in_(managed_ids))

    if status:
        stmt = stmt.where(LeaveRequest.status == status)
    else:
        current_year = datetime.now().year
        stmt = stmt.where(
            LeaveRequest.start_date >= date(current_year, 1, 1),
            LeaveRequest.start_date <= date(current_year, 12, 31),
        )

    stmt = stmt.order_by(LeaveRequest.start_date.desc())
    rows = (await session.execute(stmt)).scalars().all()

    emp_ids = list({r.employee_id for r in rows})
    name_map = await _get_employee_name_map(session, emp_ids)
    return [
        TeamLeaveRequestResponse(
            request_id=r.id,
            employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            leave_type=r.leave_type,
            start_date=r.start_date,
            end_date=r.end_date,
            days=r.days,
            reason=r.reason,
            status=r.status,
        )
        for r in rows
    ]


async def get_team_leave_balances(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    employee_id: int | None = None,
) -> list[TeamLeaveBalanceResponse]:
    """查询团队假期余额。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        employee_id: 指定员工 ID，为空则查全员
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    if employee_id:
        await _verify_employee_in_scope(session, employee_id, managed_ids)
        target_ids = [employee_id]
    else:
        target_ids = managed_ids

    current_year = datetime.now().year
    stmt = (
        select(LeaveBalance)
        .where(LeaveBalance.employee_id.in_(target_ids), LeaveBalance.year == current_year)
        .order_by(LeaveBalance.employee_id, LeaveBalance.leave_type)
    )
    rows = (await session.execute(stmt)).scalars().all()

    name_map = await _get_employee_name_map(session, target_ids)
    return [
        TeamLeaveBalanceResponse(
            employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            leave_type=r.leave_type,
            total_days=r.total_days,
            used_days=r.used_days,
            remaining_days=r.remaining_days,
        )
        for r in rows
    ]


async def get_team_overtime_records(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    year_month: str | None = None,
    status: str | None = None,
) -> list[TeamOvertimeRecordResponse]:
    """查询团队加班记录。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        year_month: 月份 YYYY-MM
        status: 状态过滤（待审批/已通过）
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    stmt = select(OvertimeRecord).where(OvertimeRecord.employee_id.in_(managed_ids))

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
            record_id=r.id,
            employee_id=r.employee_id,
            employee_name=name_map.get(r.employee_id, ""),
            date=r.date,
            start_time=r.start_time,
            end_time=r.end_time,
            hours=r.hours,
            type=r.type,
            status=r.status,
        )
        for r in rows
    ]


async def get_employee_profile(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    target_employee_id: int,
) -> EmployeeProfileResponse:
    """查询员工档案（基本信息 + 绩效 + 履历），含范围校验。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        target_employee_id: 目标员工 ID

    Raises:
        ForbiddenException: 目标员工不在管辖范围内
        NotFoundException: 员工不存在
    """
    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    await _verify_employee_in_scope(session, target_employee_id, managed_ids)

    info = await get_employee_info(session, target_employee_id)

    perf_stmt = (
        select(PerformanceReview)
        .where(PerformanceReview.employee_id == target_employee_id)
        .order_by(PerformanceReview.year.desc(), PerformanceReview.half.desc())
    )
    perf_rows = (await session.execute(perf_stmt)).scalars().all()

    hist_stmt = (
        select(EmploymentHistory)
        .where(EmploymentHistory.employee_id == target_employee_id)
        .order_by(EmploymentHistory.start_date.desc())
    )
    hist_rows = (await session.execute(hist_stmt)).scalars().all()

    return EmployeeProfileResponse(
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
    )


async def approve_leave_request(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    request_id: int,
    action: str,
    comment: str = "",
) -> ApprovalResponse:
    """审批请假申请。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        request_id: 请假申请 ID
        action: 通过/拒绝
        comment: 审批备注

    Raises:
        NotFoundException: 申请不存在
        ForbiddenException: 无权审批
    """
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

    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    if leave_req.employee_id not in managed_ids:
        return ApprovalResponse(
            success=False,
            message="该员工不在您的管辖范围内，无权审批",
        )

    new_status = "已通过" if action == "通过" else "已拒绝"
    leave_req.status = new_status
    await session.commit()

    return ApprovalResponse(
        success=True,
        request_id=request_id,
        action=action,
        message=f"请假申请已{action}",
    )


async def approve_overtime_request(
    session: AsyncSession,
    manager_employee_id: int,
    department_id: int,
    record_id: int,
    action: str,
    comment: str = "",
) -> ApprovalResponse:
    """审批加班申请。

    Args:
        session: 数据库会话
        manager_employee_id: 主管的员工 ID
        department_id: 主管管辖的部门 ID
        record_id: 加班记录 ID
        action: 通过/拒绝
        comment: 审批备注

    Raises:
        NotFoundException: 记录不存在
        ForbiddenException: 无权审批
    """
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

    managed_ids = await get_managed_employee_ids(session, manager_employee_id, department_id)
    if ot_record.employee_id not in managed_ids:
        return ApprovalResponse(
            success=False,
            message="该员工不在您的管辖范围内，无权审批",
        )

    new_status = "已通过" if action == "通过" else "已拒绝"
    ot_record.status = new_status
    await session.commit()

    return ApprovalResponse(
        success=True,
        request_id=record_id,
        action=action,
        message=f"加班申请已{action}",
    )


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
    return await get_salary_records(session, employee_id, year_month)


async def get_any_employee_social_insurance(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[SocialInsuranceResponse]:
    """查询任意员工的社保明细（管理者专用）。"""
    return await get_social_insurance(session, employee_id, year_month)


async def get_any_employee_profile(
    session: AsyncSession, target_employee_id: int,
) -> EmployeeFullProfileResponse:
    """查询任意员工的完整档案（含薪资社保，管理者专用）。

    Raises:
        NotFoundException: 员工不存在
    """
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


# ── 人才发展 Service ─────────────────────────────────────────


async def get_employee_training(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[TrainingResponse]:
    """查询任意员工的培训记录。"""
    stmt = select(Training).where(Training.employee_id == employee_id)
    if status:
        stmt = stmt.where(Training.status == status)
    stmt = stmt.order_by(Training.completed_date.desc().nullslast(), Training.deadline.desc().nullslast())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        TrainingResponse(
            course_name=r.course_name, category=r.category, hours=r.hours,
            score=r.score, status=r.status, provider=r.provider,
            assigned_by=r.assigned_by, deadline=r.deadline, completed_date=r.completed_date,
        )
        for r in rows
    ]


async def get_employee_talent_review(
    session: AsyncSession, employee_id: int, review_year: int | None = None,
) -> list[TalentReviewResponse]:
    """查询任意员工的人才盘点历史。"""
    stmt = select(TalentReview).where(TalentReview.employee_id == employee_id)
    if review_year:
        stmt = stmt.where(TalentReview.review_year == review_year)
    stmt = stmt.order_by(TalentReview.review_year.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        TalentReviewResponse(
            review_year=r.review_year, performance=r.performance, potential=r.potential,
            nine_grid_pos=r.nine_grid_pos, tag=r.tag, reviewer=r.reviewer, comment=r.comment,
        )
        for r in rows
    ]


async def get_employee_idp(
    session: AsyncSession, employee_id: int, plan_year: int | None = None,
) -> list[DevelopmentPlanResponse]:
    """查询任意员工的个人发展计划。"""
    stmt = select(DevelopmentPlan).where(DevelopmentPlan.employee_id == employee_id)
    if plan_year:
        stmt = stmt.where(DevelopmentPlan.plan_year == plan_year)
    stmt = stmt.order_by(DevelopmentPlan.plan_year.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        DevelopmentPlanResponse(
            plan_year=r.plan_year, goal=r.goal, category=r.category,
            actions=r.actions, status=r.status, progress=r.progress, deadline=r.deadline,
        )
        for r in rows
    ]


async def get_employee_performance_detail(
    session: AsyncSession, employee_id: int,
) -> list[PerformanceReviewResponse]:
    """查询任意员工的绩效详情（含评语分数）。"""
    stmt = (
        select(PerformanceReview)
        .where(PerformanceReview.employee_id == employee_id)
        .order_by(PerformanceReview.year.desc(), PerformanceReview.half.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        PerformanceReviewResponse(
            year=r.year, half=r.half, rating=r.rating,
            score=r.score, reviewer=r.reviewer, comment=r.comment,
        )
        for r in rows
    ]


async def get_employee_employment_history(
    session: AsyncSession, employee_id: int,
) -> list[EmploymentHistoryResponse]:
    """查询任意员工的岗位变动履历。"""
    stmt = (
        select(EmploymentHistory)
        .where(EmploymentHistory.employee_id == employee_id)
        .order_by(EmploymentHistory.start_date.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        EmploymentHistoryResponse(
            start_date=r.start_date, end_date=r.end_date, department=r.department,
            position=r.position, level=r.level, change_type=r.change_type, remark=r.remark,
        )
        for r in rows
    ]


async def get_employee_attendance_records(
    session: AsyncSession, employee_id: int,
    start_date: str | None = None, end_date: str | None = None,
) -> list[AttendanceResponse]:
    """查询任意员工的考勤记录。"""
    stmt = select(AttendanceRecord).where(AttendanceRecord.employee_id == employee_id)
    if start_date:
        stmt = stmt.where(AttendanceRecord.date >= date.fromisoformat(start_date))
    else:
        stmt = stmt.where(AttendanceRecord.date >= date.today().replace(day=1))
    if end_date:
        stmt = stmt.where(AttendanceRecord.date <= date.fromisoformat(end_date))
    stmt = stmt.order_by(AttendanceRecord.date.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        AttendanceResponse(
            date=r.date, check_in=r.check_in, check_out=r.check_out,
            status=r.status, remark=r.remark,
        )
        for r in rows
    ]


# ── 人才发展报表 Service ─────────────────────────────────────


async def get_training_summary(
    session: AsyncSession, year: int | None = None,
) -> list[TrainingSummaryResponse]:
    """各部门培训统计。"""
    employees = (await session.execute(select(Employee))).scalars().all()
    depts = (await session.execute(select(Department))).scalars().all()
    dept_name = {d.id: d.name for d in depts}

    stmt = select(Training)
    if year:
        y_start = date(year, 1, 1).isoformat()
        y_end = date(year, 12, 31).isoformat()
        stmt = stmt.where(
            ((Training.completed_date >= y_start) & (Training.completed_date <= y_end))
            | ((Training.deadline >= y_start) & (Training.deadline <= y_end))
        )
    trainings = (await session.execute(stmt)).scalars().all()

    emp_dept = {e.id: e.department_id for e in employees}
    dept_emp_count: dict[int, int] = {}
    for e in employees:
        if e.status in ("在职", "试用期") and e.department_id:
            dept_emp_count[e.department_id] = dept_emp_count.get(e.department_id, 0) + 1

    dept_stats: dict[int, dict] = {}
    for t in trainings:
        did = emp_dept.get(t.employee_id, 0)
        if did not in dept_stats:
            dept_stats[did] = {"completed": 0, "total_hours": 0, "mandatory_total": 0, "mandatory_done": 0}
        if t.status == "已完成":
            dept_stats[did]["completed"] += 1
            dept_stats[did]["total_hours"] += float(t.hours)
        if t.category == "合规必修":
            dept_stats[did]["mandatory_total"] += 1
            if t.status == "已完成":
                dept_stats[did]["mandatory_done"] += 1

    results = []
    for did in sorted(dept_emp_count.keys()):
        stats = dept_stats.get(did, {"completed": 0, "total_hours": 0, "mandatory_total": 0, "mandatory_done": 0})
        emp_count = dept_emp_count[did]
        results.append(TrainingSummaryResponse(
            department_id=did,
            department_name=dept_name.get(did, "未知"),
            total_employees=emp_count,
            completed_count=stats["completed"],
            completion_rate=round(stats["completed"] / max(emp_count, 1), 2),
            total_hours=round(stats["total_hours"], 1),
            avg_hours=round(stats["total_hours"] / max(emp_count, 1), 1),
            mandatory_completion_rate=round(
                stats["mandatory_done"] / max(stats["mandatory_total"], 1), 2
            ),
        ))
    return results


async def get_nine_grid_distribution(
    session: AsyncSession, review_year: int | None = None, department_id: int | None = None,
) -> NineGridDistributionResponse:
    """九宫格分布统计。"""
    ry = review_year or date.today().year - 1
    stmt = select(TalentReview).where(TalentReview.review_year == ry)
    reviews = (await session.execute(stmt)).scalars().all()

    if department_id:
        emp_ids_in_dept = {
            e.id for e in (await session.execute(
                select(Employee).where(Employee.department_id == department_id)
            )).scalars().all()
        }
        reviews = [r for r in reviews if r.employee_id in emp_ids_in_dept]

    distribution: dict[str, int] = {}
    for r in reviews:
        distribution[r.nine_grid_pos] = distribution.get(r.nine_grid_pos, 0) + 1

    # 高潜人才清单
    hi_pot_reviews = [r for r in reviews if r.tag in ("高潜", "继任候选")]
    emp_ids = list({r.employee_id for r in hi_pot_reviews})
    emp_map = {}
    if emp_ids:
        emps = (await session.execute(select(Employee).where(Employee.id.in_(emp_ids)))).scalars().all()
        emp_map = {e.id: e for e in emps}

    hi_pot_list = []
    for r in hi_pot_reviews:
        e = emp_map.get(r.employee_id)
        if e:
            hi_pot_list.append({
                "employee_id": e.id, "name": e.name, "position": e.position,
                "level": e.level, "nine_grid_pos": r.nine_grid_pos, "tag": r.tag,
            })

    return NineGridDistributionResponse(distribution=distribution, high_potential_employees=hi_pot_list)


async def get_performance_distribution(
    session: AsyncSession, year: int | None = None, half: str | None = None,
) -> list[PerformanceDistributionResponse]:
    """各部门绩效评级分布。"""
    yr = year or date.today().year - 1
    stmt = select(PerformanceReview).where(PerformanceReview.year == yr)
    if half:
        stmt = stmt.where(PerformanceReview.half == half)
    reviews = (await session.execute(stmt)).scalars().all()

    employees = (await session.execute(select(Employee))).scalars().all()
    emp_dept = {e.id: e.department_id for e in employees}
    depts = (await session.execute(select(Department))).scalars().all()
    dept_name = {d.id: d.name for d in depts}

    dept_ratings: dict[int, dict[str, int]] = {}
    for r in reviews:
        did = emp_dept.get(r.employee_id, 0)
        if did not in dept_ratings:
            dept_ratings[did] = {}
        dept_ratings[did][r.rating] = dept_ratings[did].get(r.rating, 0) + 1

    results = []
    for did in sorted(dept_ratings.keys()):
        ratings = dept_ratings[did]
        total = sum(ratings.values())
        percentages = {k: round(v / total * 100, 1) for k, v in ratings.items()} if total else {}
        results.append(PerformanceDistributionResponse(
            department_id=did,
            department_name=dept_name.get(did, "未知"),
            ratings=ratings,
            percentages=percentages,
        ))
    return results


async def get_turnover_analysis(session: AsyncSession) -> list[TurnoverAnalysisResponse]:
    """各部门人员流动分析。"""
    employees = (await session.execute(select(Employee))).scalars().all()
    depts = (await session.execute(select(Department))).scalars().all()
    dept_name = {d.id: d.name for d in depts}

    # 统计转正记录
    hist_rows = (await session.execute(
        select(EmploymentHistory).where(EmploymentHistory.change_type == "转正")
    )).scalars().all()
    converted_eids = {h.employee_id for h in hist_rows}

    dept_stats: dict[int, dict] = {}
    today = date.today()
    for e in employees:
        did = e.department_id or 0
        if did not in dept_stats:
            dept_stats[did] = {"total": 0, "active": 0, "resigned": 0, "probation": 0, "converted": 0, "tenure_sum": 0}
        dept_stats[did]["total"] += 1
        if e.status == "在职":
            dept_stats[did]["active"] += 1
        elif e.status == "离职":
            dept_stats[did]["resigned"] += 1
        elif e.status == "试用期":
            dept_stats[did]["probation"] += 1
        if e.id in converted_eids:
            dept_stats[did]["converted"] += 1
        if e.hire_date:
            dept_stats[did]["tenure_sum"] += (today - e.hire_date).days / 365.25

    results = []
    for did in sorted(dept_stats.keys()):
        s = dept_stats[did]
        total_for_rate = s["active"] + s["resigned"]
        probation_total = s["probation"] + s["converted"]
        results.append(TurnoverAnalysisResponse(
            department_id=did,
            department_name=dept_name.get(did, "未知"),
            total_count=s["total"],
            active_count=s["active"],
            resigned_count=s["resigned"],
            turnover_rate=round(s["resigned"] / max(total_for_rate, 1), 3),
            probation_conversion_rate=round(s["converted"] / max(probation_total, 1), 3),
            avg_tenure_years=round(s["tenure_sum"] / max(s["total"], 1), 1),
        ))
    return results


async def get_promotion_stats(
    session: AsyncSession, year: int | None = None,
) -> list[PromotionStatsResponse]:
    """各部门晋升/调岗统计。"""
    yr = year or date.today().year - 1
    yr_start = date(yr, 1, 1)
    yr_end = date(yr, 12, 31)

    hist_rows = (await session.execute(
        select(EmploymentHistory)
        .where(EmploymentHistory.start_date >= yr_start)
        .where(EmploymentHistory.start_date <= yr_end)
    )).scalars().all()

    employees = (await session.execute(select(Employee))).scalars().all()
    emp_dept = {e.id: e.department_id for e in employees}
    active_by_dept: dict[int, int] = {}
    for e in employees:
        if e.status in ("在职", "试用期") and e.department_id:
            active_by_dept[e.department_id] = active_by_dept.get(e.department_id, 0) + 1

    depts = (await session.execute(select(Department))).scalars().all()
    dept_name = {d.id: d.name for d in depts}

    dept_stats: dict[int, dict] = {}
    for h in hist_rows:
        did = emp_dept.get(h.employee_id, 0)
        if did not in dept_stats:
            dept_stats[did] = {"promotion": 0, "transfer_in": 0, "transfer_out": 0}
        if h.change_type == "晋升":
            dept_stats[did]["promotion"] += 1
        elif h.change_type == "调岗":
            # 当前部门算调入
            dept_stats[did]["transfer_in"] += 1

    results = []
    for did in sorted(set(list(active_by_dept.keys()) + list(dept_stats.keys()))):
        s = dept_stats.get(did, {"promotion": 0, "transfer_in": 0, "transfer_out": 0})
        emp_count = active_by_dept.get(did, 0)
        results.append(PromotionStatsResponse(
            department_id=did,
            department_name=dept_name.get(did, "未知"),
            promotion_count=s["promotion"],
            transfer_in_count=s["transfer_in"],
            transfer_out_count=s["transfer_out"],
            promotion_rate=round(s["promotion"] / max(emp_count, 1), 3),
        ))
    return results


async def get_idp_summary(
    session: AsyncSession, plan_year: int | None = None,
) -> IdpSummaryResponse:
    """IDP 汇总统计。"""
    yr = plan_year or date.today().year
    stmt = select(DevelopmentPlan).where(DevelopmentPlan.plan_year == yr)
    plans = (await session.execute(stmt)).scalars().all()

    total = len(plans)
    completed = sum(1 for p in plans if p.status == "已完成")
    avg_progress = round(sum(p.progress for p in plans) / max(total, 1), 1)
    cat_dist: dict[str, int] = {}
    for p in plans:
        cat_dist[p.category] = cat_dist.get(p.category, 0) + 1

    return IdpSummaryResponse(
        total_plans=total,
        completed_count=completed,
        completion_rate=round(completed / max(total, 1), 3),
        avg_progress=avg_progress,
        category_distribution=cat_dist,
    )


# ── 人才发现基础 CRUD ─────────────────────────────────────────


async def get_employee_skills(
    session: AsyncSession, employee_id: int, category: str | None = None,
) -> list[SkillResponse]:
    """查询员工技能标签。"""
    stmt = select(Skill).where(Skill.employee_id == employee_id)
    if category:
        stmt = stmt.where(Skill.category == category)
    stmt = stmt.order_by(Skill.category, Skill.name)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        SkillResponse(
            name=r.name, category=r.category, level=r.level,
            source=r.source, verified=r.verified,
        )
        for r in rows
    ]


async def get_employee_education(
    session: AsyncSession, employee_id: int,
) -> list[EducationResponse]:
    """查询员工教育背景。"""
    stmt = (
        select(Education)
        .where(Education.employee_id == employee_id)
        .order_by(Education.graduation_year.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        EducationResponse(
            degree=r.degree, major=r.major, school=r.school,
            graduation_year=r.graduation_year,
        )
        for r in rows
    ]


async def get_employee_projects(
    session: AsyncSession, employee_id: int, role: str | None = None,
) -> list[ProjectExperienceResponse]:
    """查询员工项目经历。"""
    stmt = select(ProjectExperience).where(ProjectExperience.employee_id == employee_id)
    if role:
        stmt = stmt.where(ProjectExperience.role == role)
    stmt = stmt.order_by(ProjectExperience.start_date.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        ProjectExperienceResponse(
            project_name=r.project_name, role=r.role,
            start_date=r.start_date, end_date=r.end_date,
            description=r.description, achievement=r.achievement,
        )
        for r in rows
    ]


async def get_employee_certificates(
    session: AsyncSession, employee_id: int, category: str | None = None,
) -> list[CertificateResponse]:
    """查询员工证书认证。"""
    stmt = select(Certificate).where(Certificate.employee_id == employee_id)
    if category:
        stmt = stmt.where(Certificate.category == category)
    stmt = stmt.order_by(Certificate.issue_date.desc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        CertificateResponse(
            name=r.name, issuer=r.issuer, issue_date=r.issue_date,
            expiry_date=r.expiry_date, category=r.category,
        )
        for r in rows
    ]
