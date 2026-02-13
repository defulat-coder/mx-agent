"""人才发现引擎 Service — 规则筛选 + 数据聚合"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr import (
    Certificate,
    Department,
    DevelopmentPlan,
    Education,
    Employee,
    EmploymentHistory,
    OvertimeRecord,
    PerformanceReview,
    ProjectExperience,
    Skill,
    TalentReview,
    Training,
)
from app.schemas.discovery import (
    CandidateMatchItem,
    CandidateMatchResult,
    FlightRiskCandidate,
    FlightRiskResult,
    HiddenTalentCandidate,
    HiddenTalentResult,
    PromotionReadinessItem,
    PromotionReadinessResult,
    SkillCoverage,
    TalentPortraitResult,
    TeamCapabilityGapResult,
)
from app.schemas.hr import (
    CertificateResponse,
    DevelopmentPlanResponse,
    EducationResponse,
    EmployeeInfoResponse,
    EmploymentHistoryResponse,
    PerformanceReviewResponse,
    ProjectExperienceResponse,
    SkillResponse,
    TalentReviewResponse,
    TrainingResponse,
)
from app.services.hr import get_employee_info


async def _get_active_employees(
    session: AsyncSession, department_id: int | None = None,
) -> list[Employee]:
    """获取在职员工列表。"""
    stmt = select(Employee).where(Employee.status.in_(["在职", "试用期"]))
    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    return list((await session.execute(stmt)).scalars().all())


async def discover_hidden_talent(
    session: AsyncSession, department_id: int | None = None,
) -> HiddenTalentResult:
    """被埋没高潜识别：绩效优秀 + 培训活跃 + IDP 完成率高，但标签低估。"""
    employees = await _get_active_employees(session, department_id)
    if not employees:
        return HiddenTalentResult(candidates=[], total=0)

    emp_ids = [e.id for e in employees]

    # 批量加载数据
    perfs = (await session.execute(
        select(PerformanceReview).where(PerformanceReview.employee_id.in_(emp_ids))
    )).scalars().all()
    trainings = (await session.execute(
        select(Training).where(Training.employee_id.in_(emp_ids))
    )).scalars().all()
    idps = (await session.execute(
        select(DevelopmentPlan).where(DevelopmentPlan.employee_id.in_(emp_ids))
    )).scalars().all()
    reviews = (await session.execute(
        select(TalentReview).where(TalentReview.employee_id.in_(emp_ids))
    )).scalars().all()

    # 按员工分组
    perf_by_emp: dict[int, list[PerformanceReview]] = {}
    for p in perfs:
        perf_by_emp.setdefault(p.employee_id, []).append(p)
    train_by_emp: dict[int, list[Training]] = {}
    for t in trainings:
        train_by_emp.setdefault(t.employee_id, []).append(t)
    idp_by_emp: dict[int, list[DevelopmentPlan]] = {}
    for i in idps:
        idp_by_emp.setdefault(i.employee_id, []).append(i)
    review_by_emp: dict[int, list[TalentReview]] = {}
    for r in reviews:
        review_by_emp.setdefault(r.employee_id, []).append(r)

    candidates = []
    good_ratings = {"A", "B+"}

    for emp in employees:
        emp_perfs = perf_by_emp.get(emp.id, [])
        emp_perfs.sort(key=lambda p: (p.year, p.half))

        # 条件1: 连续 2 期 >= B+
        if len(emp_perfs) < 2:
            continue
        recent_perfs = emp_perfs[-4:]  # 最多看近 4 期
        recent_ratings = [p.rating for p in recent_perfs]
        consecutive_good = sum(1 for r in recent_ratings[-2:] if r in good_ratings)
        if consecutive_good < 2:
            continue

        # 条件2: 自主报名培训 >= 3
        emp_trains = train_by_emp.get(emp.id, [])
        self_initiated = [t for t in emp_trains if t.assigned_by == "" and t.status == "已完成"]
        if len(self_initiated) < 3:
            continue

        # 条件3: IDP 完成率 > 70%
        emp_idps = idp_by_emp.get(emp.id, [])
        if not emp_idps:
            continue
        completed_idps = sum(1 for i in emp_idps if i.status == "已完成")
        idp_rate = completed_idps / len(emp_idps)
        if idp_rate <= 0.7:
            continue

        # 条件4: 九宫格标签为普通或位置为中坚及以下
        emp_reviews = review_by_emp.get(emp.id, [])
        latest_review = max(emp_reviews, key=lambda r: r.review_year) if emp_reviews else None
        current_tag = latest_review.tag if latest_review else "无"
        current_pos = latest_review.nine_grid_pos if latest_review else "无"

        low_tags = {"普通", "无"}
        low_positions = {"中坚", "待雕琢", "专家", "待观察", "淘汰区", "无"}
        if current_tag not in low_tags and current_pos not in low_positions:
            continue

        info = await get_employee_info(session, emp.id)
        signals = []
        signals.append(f"绩效连续优秀: {', '.join(recent_ratings[-2:])}")
        signals.append(f"自主完成培训 {len(self_initiated)} 门")
        signals.append(f"IDP 完成率 {idp_rate:.0%}")
        if current_tag in low_tags:
            signals.append(f"当前标签「{current_tag}」可能被低估")

        candidates.append(HiddenTalentCandidate(
            info=info,
            performance_trend=recent_ratings,
            self_initiated_training_count=len(self_initiated),
            idp_completion_rate=round(idp_rate, 2),
            current_nine_grid=current_pos,
            current_tag=current_tag,
            signals=signals,
        ))

    return HiddenTalentResult(candidates=candidates, total=len(candidates))


async def assess_flight_risk(
    session: AsyncSession, department_id: int | None = None,
) -> FlightRiskResult:
    """流失风险预警：高绩效 + 职级停留 + IDP 状态 + 加班趋势。"""
    employees = await _get_active_employees(session, department_id)
    if not employees:
        return FlightRiskResult(candidates=[], total=0)

    emp_ids = [e.id for e in employees]

    perfs = (await session.execute(
        select(PerformanceReview).where(PerformanceReview.employee_id.in_(emp_ids))
    )).scalars().all()
    histories = (await session.execute(
        select(EmploymentHistory).where(EmploymentHistory.employee_id.in_(emp_ids))
    )).scalars().all()
    idps = (await session.execute(
        select(DevelopmentPlan).where(DevelopmentPlan.employee_id.in_(emp_ids))
    )).scalars().all()
    overtimes = (await session.execute(
        select(OvertimeRecord).where(OvertimeRecord.employee_id.in_(emp_ids))
    )).scalars().all()

    perf_by_emp: dict[int, list[PerformanceReview]] = {}
    for p in perfs:
        perf_by_emp.setdefault(p.employee_id, []).append(p)
    hist_by_emp: dict[int, list[EmploymentHistory]] = {}
    for h in histories:
        hist_by_emp.setdefault(h.employee_id, []).append(h)
    idp_by_emp: dict[int, list[DevelopmentPlan]] = {}
    for i in idps:
        idp_by_emp.setdefault(i.employee_id, []).append(i)
    ot_by_emp: dict[int, list[OvertimeRecord]] = {}
    for o in overtimes:
        ot_by_emp.setdefault(o.employee_id, []).append(o)

    good_ratings = {"A", "B+"}
    today = date.today()
    candidates = []

    for emp in employees:
        # 条件1: 高绩效
        emp_perfs = perf_by_emp.get(emp.id, [])
        if not emp_perfs:
            continue
        emp_perfs.sort(key=lambda p: (p.year, p.half))
        latest_rating = emp_perfs[-1].rating
        if latest_rating not in good_ratings:
            continue

        # 条件2: 职级停留 >= 2 年
        emp_hists = hist_by_emp.get(emp.id, [])
        emp_hists.sort(key=lambda h: h.start_date)
        current_hist = emp_hists[-1] if emp_hists else None
        if current_hist:
            level_tenure = (today - current_hist.start_date).days / 365.25
        else:
            level_tenure = (today - emp.hire_date).days / 365.25 if emp.hire_date else 0
        if level_tenure < 2:
            continue

        # 条件3: 无活跃 IDP 或 IDP 已放弃
        emp_idps = idp_by_emp.get(emp.id, [])
        active_idps = [i for i in emp_idps if i.status == "进行中"]
        abandoned_idps = [i for i in emp_idps if i.status == "已放弃"]
        idp_status = "无" if not emp_idps else ("已放弃" if abandoned_idps and not active_idps else "进行中" if active_idps else "已完成")
        if idp_status not in ("无", "已放弃"):
            continue

        # 加班统计（近 3 个月）
        three_months_ago = date(today.year, max(today.month - 3, 1), 1) if today.month > 3 else date(today.year - 1, today.month + 9, 1)
        emp_ots = ot_by_emp.get(emp.id, [])
        recent_ot_hours = sum(float(o.hours) for o in emp_ots if o.date >= three_months_ago)

        risk_signals = []
        risk_signals.append(f"高绩效({latest_rating})但职级停留 {level_tenure:.1f} 年")
        risk_signals.append(f"IDP 状态: {idp_status}")
        if recent_ot_hours > 60:
            risk_signals.append(f"近 3 月加班 {recent_ot_hours:.0f} 小时，可能疲劳")

        recent_ratings = [p.rating for p in emp_perfs[-3:]]
        info = await get_employee_info(session, emp.id)
        candidates.append(FlightRiskCandidate(
            info=info,
            performance_ratings=recent_ratings,
            level_tenure_years=round(level_tenure, 1),
            idp_status=idp_status,
            recent_overtime_hours=round(recent_ot_hours, 1),
            risk_signals=risk_signals,
        ))

    return FlightRiskResult(candidates=candidates, total=len(candidates))


async def evaluate_promotion_readiness(
    session: AsyncSession,
    employee_id: int | None = None,
    department_id: int | None = None,
) -> PromotionReadinessResult:
    """晋升准备度评估：综合评分 1-100。"""
    if employee_id:
        emp = (await session.execute(
            select(Employee).where(Employee.id == employee_id)
        )).scalar_one_or_none()
        employees = [emp] if emp else []
    else:
        employees = await _get_active_employees(session, department_id)

    if not employees:
        return PromotionReadinessResult(items=[])

    emp_ids = [e.id for e in employees]
    today = date.today()

    perfs = (await session.execute(
        select(PerformanceReview).where(PerformanceReview.employee_id.in_(emp_ids))
    )).scalars().all()
    histories = (await session.execute(
        select(EmploymentHistory).where(EmploymentHistory.employee_id.in_(emp_ids))
    )).scalars().all()
    trainings = (await session.execute(
        select(Training).where(
            Training.employee_id.in_(emp_ids),
            Training.category == "管理能力",
            Training.status == "已完成",
        )
    )).scalars().all()
    idps = (await session.execute(
        select(DevelopmentPlan).where(DevelopmentPlan.employee_id.in_(emp_ids))
    )).scalars().all()

    perf_by_emp: dict[int, list[PerformanceReview]] = {}
    for p in perfs:
        perf_by_emp.setdefault(p.employee_id, []).append(p)
    hist_by_emp: dict[int, list[EmploymentHistory]] = {}
    for h in histories:
        hist_by_emp.setdefault(h.employee_id, []).append(h)
    train_by_emp: dict[int, list[Training]] = {}
    for t in trainings:
        train_by_emp.setdefault(t.employee_id, []).append(t)
    idp_by_emp: dict[int, list[DevelopmentPlan]] = {}
    for i in idps:
        idp_by_emp.setdefault(i.employee_id, []).append(i)

    rating_scores = {"A": 100, "B+": 80, "B": 60, "C": 30, "D": 0}

    items = []
    for emp in employees:
        # 职级停留时长评分 (25%)
        emp_hists = hist_by_emp.get(emp.id, [])
        emp_hists.sort(key=lambda h: h.start_date)
        current_hist = emp_hists[-1] if emp_hists else None
        if current_hist:
            tenure = (today - current_hist.start_date).days / 365.25
        else:
            tenure = (today - emp.hire_date).days / 365.25 if emp.hire_date else 0
        tenure_score = min(tenure / 2 * 100, 100)

        # 最近绩效评分 (30%)
        emp_perfs = perf_by_emp.get(emp.id, [])
        emp_perfs.sort(key=lambda p: (p.year, p.half))
        latest_rating = emp_perfs[-1].rating if emp_perfs else "B"
        perf_score = rating_scores.get(latest_rating, 60)

        # 管理培训评分 (20%)
        mgmt_trains = train_by_emp.get(emp.id, [])
        mgmt_score = min(len(mgmt_trains) / 3 * 100, 100)

        # IDP 完成度评分 (25%)
        emp_idps = idp_by_emp.get(emp.id, [])
        avg_progress = sum(i.progress for i in emp_idps) / max(len(emp_idps), 1)
        idp_score = avg_progress

        readiness = int(tenure_score * 0.25 + perf_score * 0.30 + mgmt_score * 0.20 + idp_score * 0.25)
        readiness = max(1, min(100, readiness))

        info = await get_employee_info(session, emp.id)
        items.append(PromotionReadinessItem(
            info=info,
            level_tenure_years=round(tenure, 1),
            latest_rating=latest_rating,
            management_training_count=len(mgmt_trains),
            idp_progress=int(avg_progress),
            readiness_score=readiness,
        ))

    items.sort(key=lambda x: x.readiness_score, reverse=True)
    return PromotionReadinessResult(items=items)


async def find_candidates(
    session: AsyncSession, requirements: str,
) -> CandidateMatchResult:
    """岗位适配推荐：基于技能 + 项目 + 培训关键词匹配。"""
    keywords = [kw.strip() for kw in requirements.replace("，", ",").replace("、", ",").split(",") if kw.strip()]
    if not keywords:
        keywords = requirements.split()

    employees = await _get_active_employees(session)
    if not employees:
        return CandidateMatchResult(candidates=[], total=0, notice="无在职员工")

    emp_ids = [e.id for e in employees]

    skills = (await session.execute(
        select(Skill).where(Skill.employee_id.in_(emp_ids))
    )).scalars().all()
    projects = (await session.execute(
        select(ProjectExperience).where(ProjectExperience.employee_id.in_(emp_ids))
    )).scalars().all()
    trainings = (await session.execute(
        select(Training).where(Training.employee_id.in_(emp_ids), Training.status == "已完成")
    )).scalars().all()
    perfs = (await session.execute(
        select(PerformanceReview).where(PerformanceReview.employee_id.in_(emp_ids))
    )).scalars().all()

    skill_by_emp: dict[int, list[Skill]] = {}
    for s in skills:
        skill_by_emp.setdefault(s.employee_id, []).append(s)
    proj_by_emp: dict[int, list[ProjectExperience]] = {}
    for p in projects:
        proj_by_emp.setdefault(p.employee_id, []).append(p)
    train_by_emp: dict[int, list[Training]] = {}
    for t in trainings:
        train_by_emp.setdefault(t.employee_id, []).append(t)
    perf_by_emp: dict[int, list[PerformanceReview]] = {}
    for p in perfs:
        perf_by_emp.setdefault(p.employee_id, []).append(p)

    has_skill_data = len(skills) > 0
    notice = "" if has_skill_data else "技能数据不足，建议先完善员工技能标签。当前基于培训和项目经历做有限匹配。"

    scored: list[tuple[Employee, int, list[str], list[str], str]] = []
    for emp in employees:
        score = 0
        matched_skills: list[str] = []
        relevant_projects: list[str] = []

        # 技能匹配
        emp_skills = skill_by_emp.get(emp.id, [])
        for s in emp_skills:
            for kw in keywords:
                if kw.lower() in s.name.lower():
                    level_bonus = {"专家": 4, "高级": 3, "中级": 2, "初级": 1}.get(s.level, 1)
                    score += 10 * level_bonus
                    matched_skills.append(f"{s.name}({s.level})")

        # 项目匹配
        emp_projs = proj_by_emp.get(emp.id, [])
        for p in emp_projs:
            text = f"{p.project_name} {p.description} {p.achievement}"
            for kw in keywords:
                if kw.lower() in text.lower():
                    role_bonus = {"负责人": 3, "核心成员": 2, "参与者": 1}.get(p.role, 1)
                    score += 5 * role_bonus
                    if p.project_name not in relevant_projects:
                        relevant_projects.append(p.project_name)
                    break

        # 培训匹配
        emp_trains = train_by_emp.get(emp.id, [])
        for t in emp_trains:
            for kw in keywords:
                if kw.lower() in t.course_name.lower():
                    score += 2
                    break

        if score == 0:
            continue

        # 绩效基线
        emp_perfs = perf_by_emp.get(emp.id, [])
        emp_perfs.sort(key=lambda p: (p.year, p.half))
        latest_rating = emp_perfs[-1].rating if emp_perfs else "B"
        if latest_rating in ("C", "D"):
            continue

        scored.append((emp, score, matched_skills, relevant_projects, latest_rating))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:20]

    candidates = []
    for emp, score, matched_skills, relevant_projects, latest_rating in top:
        info = await get_employee_info(session, emp.id)
        summary_parts = []
        if matched_skills:
            summary_parts.append(f"技能匹配: {', '.join(matched_skills)}")
        if relevant_projects:
            summary_parts.append(f"相关项目: {', '.join(relevant_projects[:3])}")
        candidates.append(CandidateMatchItem(
            info=info,
            matched_skills=matched_skills,
            relevant_projects=relevant_projects,
            latest_rating=latest_rating,
            match_summary="; ".join(summary_parts) if summary_parts else "基于培训记录匹配",
        ))

    return CandidateMatchResult(candidates=candidates, total=len(candidates), notice=notice)


async def build_talent_portrait(
    session: AsyncSession, employee_id: int,
) -> TalentPortraitResult:
    """完整人才画像：汇总所有维度数据。"""
    info = await get_employee_info(session, employee_id)

    edu_rows = (await session.execute(
        select(Education).where(Education.employee_id == employee_id).order_by(Education.graduation_year.desc())
    )).scalars().all()
    skill_rows = (await session.execute(
        select(Skill).where(Skill.employee_id == employee_id).order_by(Skill.category)
    )).scalars().all()
    proj_rows = (await session.execute(
        select(ProjectExperience).where(ProjectExperience.employee_id == employee_id).order_by(ProjectExperience.start_date.desc())
    )).scalars().all()
    cert_rows = (await session.execute(
        select(Certificate).where(Certificate.employee_id == employee_id).order_by(Certificate.issue_date.desc())
    )).scalars().all()
    perf_rows = (await session.execute(
        select(PerformanceReview).where(PerformanceReview.employee_id == employee_id).order_by(PerformanceReview.year.desc(), PerformanceReview.half.desc())
    )).scalars().all()
    train_rows = (await session.execute(
        select(Training).where(Training.employee_id == employee_id).order_by(Training.completed_date.desc().nullslast())
    )).scalars().all()
    idp_rows = (await session.execute(
        select(DevelopmentPlan).where(DevelopmentPlan.employee_id == employee_id).order_by(DevelopmentPlan.plan_year.desc())
    )).scalars().all()
    review_rows = (await session.execute(
        select(TalentReview).where(TalentReview.employee_id == employee_id).order_by(TalentReview.review_year.desc())
    )).scalars().all()
    hist_rows = (await session.execute(
        select(EmploymentHistory).where(EmploymentHistory.employee_id == employee_id).order_by(EmploymentHistory.start_date.desc())
    )).scalars().all()

    return TalentPortraitResult(
        info=info,
        educations=[EducationResponse(degree=r.degree, major=r.major, school=r.school, graduation_year=r.graduation_year) for r in edu_rows],
        skills=[SkillResponse(name=r.name, category=r.category, level=r.level, source=r.source, verified=r.verified) for r in skill_rows],
        projects=[ProjectExperienceResponse(project_name=r.project_name, role=r.role, start_date=r.start_date, end_date=r.end_date, description=r.description, achievement=r.achievement) for r in proj_rows],
        certificates=[CertificateResponse(name=r.name, issuer=r.issuer, issue_date=r.issue_date, expiry_date=r.expiry_date, category=r.category) for r in cert_rows],
        performance_reviews=[PerformanceReviewResponse(year=r.year, half=r.half, rating=r.rating, score=r.score, reviewer=r.reviewer, comment=r.comment) for r in perf_rows],
        trainings=[TrainingResponse(course_name=r.course_name, category=r.category, hours=r.hours, score=r.score, status=r.status, provider=r.provider, assigned_by=r.assigned_by, deadline=r.deadline, completed_date=r.completed_date) for r in train_rows],
        development_plans=[DevelopmentPlanResponse(plan_year=r.plan_year, goal=r.goal, category=r.category, actions=r.actions, status=r.status, progress=r.progress, deadline=r.deadline) for r in idp_rows],
        talent_reviews=[TalentReviewResponse(review_year=r.review_year, performance=r.performance, potential=r.potential, nine_grid_pos=r.nine_grid_pos, tag=r.tag, reviewer=r.reviewer, comment=r.comment) for r in review_rows],
        employment_histories=[EmploymentHistoryResponse(start_date=r.start_date, end_date=r.end_date, department=r.department, position=r.position, level=r.level, change_type=r.change_type, remark=r.remark) for r in hist_rows],
    )


async def analyze_team_capability_gap(
    session: AsyncSession, department_id: int,
) -> TeamCapabilityGapResult:
    """团队能力短板分析：技能覆盖和缺口。"""
    dept = (await session.execute(
        select(Department).where(Department.id == department_id)
    )).scalar_one_or_none()
    dept_name = dept.name if dept else "未知"

    employees = await _get_active_employees(session, department_id)
    if not employees:
        return TeamCapabilityGapResult(
            department_name=dept_name, total_employees=0,
            skill_coverage=[], high_frequency_skills=[], rare_skills=[],
            suggestions=[], notice="该部门无在职员工",
        )

    emp_ids = [e.id for e in employees]
    skills = (await session.execute(
        select(Skill).where(Skill.employee_id.in_(emp_ids))
    )).scalars().all()

    if not skills:
        # 降级：基于培训推断
        trainings = (await session.execute(
            select(Training).where(Training.employee_id.in_(emp_ids), Training.status == "已完成")
        )).scalars().all()
        cat_counts: dict[str, int] = {}
        for t in trainings:
            cat_counts[t.category] = cat_counts.get(t.category, 0) + 1
        suggestions = [f"团队培训集中在: {', '.join(sorted(cat_counts, key=cat_counts.get, reverse=True)[:3])}"] if cat_counts else []
        return TeamCapabilityGapResult(
            department_name=dept_name, total_employees=len(employees),
            skill_coverage=[], high_frequency_skills=[], rare_skills=[],
            suggestions=suggestions,
            notice="技能数据不足，建议先完善员工技能标签。以上基于培训记录推断。",
        )

    # 统计技能覆盖
    skill_stats: dict[str, dict[str, int]] = {}
    skill_emp_count: dict[str, set[int]] = {}
    for s in skills:
        if s.name not in skill_stats:
            skill_stats[s.name] = {}
            skill_emp_count[s.name] = set()
        skill_stats[s.name][s.level] = skill_stats[s.name].get(s.level, 0) + 1
        skill_emp_count[s.name].add(s.employee_id)

    coverage = [
        SkillCoverage(skill_name=name, count=len(emps), levels=levels)
        for name, (emps, levels) in (
            (n, (skill_emp_count[n], skill_stats[n])) for n in skill_stats
        )
    ]
    coverage.sort(key=lambda x: x.count, reverse=True)

    high_freq = [c.skill_name for c in coverage[:5]]
    rare = [c.skill_name for c in coverage if c.count == 1]

    suggestions = []
    if rare:
        suggestions.append(f"单点风险技能（仅1人掌握）: {', '.join(rare[:5])}，建议培养备份人才")
    emp_with_skills = len({s.employee_id for s in skills})
    if emp_with_skills < len(employees):
        suggestions.append(f"{len(employees) - emp_with_skills} 名员工尚未录入技能标签")

    return TeamCapabilityGapResult(
        department_name=dept_name, total_employees=len(employees),
        skill_coverage=coverage, high_frequency_skills=high_freq,
        rare_skills=rare, suggestions=suggestions,
    )
