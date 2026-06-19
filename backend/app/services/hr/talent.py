"""Talent-development HR queries and analytics."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr import (
    AttendanceRecord,
    Certificate,
    Department,
    DevelopmentPlan,
    Education,
    Employee,
    EmploymentHistory,
    PerformanceReview,
    ProjectExperience,
    Skill,
    TalentReview,
    Training,
)
from app.schemas.hr import (
    AttendanceResponse,
    CertificateResponse,
    DevelopmentPlanResponse,
    EducationResponse,
    EmploymentHistoryResponse,
    IdpSummaryResponse,
    NineGridDistributionResponse,
    PerformanceDistributionResponse,
    PerformanceReviewResponse,
    ProjectExperienceResponse,
    PromotionStatsResponse,
    SkillResponse,
    TalentReviewResponse,
    TrainingResponse,
    TrainingSummaryResponse,
    TurnoverAnalysisResponse,
)
from app.services.hr.admin import get_any_employee_profile


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


async def search_employee_by_name(session: AsyncSession, name: str) -> list[dict]:
    """根据姓名模糊搜索员工，返回 id、姓名、工号、部门、岗位、职级。

    Args:
        name: 员工姓名（支持模糊匹配）

    Returns:
        匹配的员工列表
    """
    stmt = (
        select(Employee, Department.name.label("dept_name"))
        .outerjoin(Department, Employee.department_id == Department.id)
        .where(Employee.name.contains(name))
        .where(Employee.status != "离职")
        .order_by(Employee.id)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "employee_id": emp.id,
            "name": emp.name,
            "employee_no": emp.employee_no,
            "department": dept_name or "",
            "position": emp.position,
            "level": emp.level,
        }
        for emp, dept_name in rows
    ]
