"""Manager-scoped HR queries and approvals."""

from datetime import date, datetime

from loguru import logger
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
)
from app.schemas.hr import (
    ApprovalResponse,
    EmployeeProfileResponse,
    EmploymentHistoryResponse,
    PerformanceReviewResponse,
    TeamAttendanceResponse,
    TeamLeaveBalanceResponse,
    TeamLeaveRequestResponse,
    TeamMemberResponse,
    TeamOvertimeRecordResponse,
)
from app.services.hr.employee import get_employee_info


async def get_managed_department_ids(session: AsyncSession, department_id: int) -> list[int]:
    """递归获取管辖部门 ID 列表（含自身），使用 PostgreSQL 递归 CTE。"""
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
    """获取管辖范围内所有员工 ID，含权限校验。"""
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
    """查询团队成员列表。"""
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
    """查询团队考勤记录。"""
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
    """查询团队请假记录。"""
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
    """查询团队假期余额。"""
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
    """查询团队加班记录。"""
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
    """查询员工档案（基本信息 + 绩效 + 履历），含范围校验。"""
    logger.info("查询员工档案 | manager={mid} target={tid}", mid=manager_employee_id, tid=target_employee_id)
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
    """审批请假申请。"""
    logger.info("审批请假 | approver={mid} request_id={rid} action={act}", mid=manager_employee_id, rid=request_id, act=action)
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
    """审批加班申请。"""
    logger.info("审批加班 | approver={mid} record_id={rid} action={act}", mid=manager_employee_id, rid=record_id, act=action)
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
