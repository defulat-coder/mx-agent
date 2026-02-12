"""HR 数据查询 Service — 封装员工薪资、考勤等只读查询，强制 employee_id 过滤"""

from datetime import date, datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.hr import (
    AttendanceRecord,
    Department,
    Employee,
    EmploymentHistory,
    LeaveBalance,
    LeaveRequest,
    OvertimeRecord,
    PerformanceReview,
    SalaryRecord,
    SocialInsuranceRecord,
)
from app.schemas.hr import (
    ApprovalResponse,
    AttendanceResponse,
    EmployeeInfoResponse,
    EmployeeProfileResponse,
    EmploymentHistoryResponse,
    LeaveBalanceResponse,
    LeaveRequestResponse,
    OvertimeRecordResponse,
    PerformanceReviewResponse,
    SalaryRecordResponse,
    SocialInsuranceResponse,
    TeamAttendanceResponse,
    TeamLeaveBalanceResponse,
    TeamLeaveRequestResponse,
    TeamMemberResponse,
    TeamOvertimeRecordResponse,
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
