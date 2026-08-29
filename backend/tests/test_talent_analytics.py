from datetime import date, timedelta
from decimal import Decimal

import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.hr import (
    Department,
    Employee,
    EmploymentHistory,
    ProjectExperience,
    Skill,
    Training,
)
from app.services.discovery import evaluate_promotion_readiness, find_candidates
from app.services.hr.talent import (
    get_promotion_stats,
    get_training_summary,
    get_turnover_analysis,
)


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session, engine
    await engine.dispose()


async def _add_department_and_employees(session, count: int = 1):
    department = Department(name="研发部", parent_id=None, manager_id=None)
    session.add(department)
    await session.flush()
    employees = [
        Employee(
            name=f"员工{i}", employee_no=f"E{i:03d}", department_id=department.id,
            position="工程师", level="P6", hire_date=date.today() - timedelta(days=1096),
            status="在职", email="", phone="",
        )
        for i in range(1, count + 1)
    ]
    session.add_all(employees)
    await session.flush()
    return department, employees


async def test_promotion_readiness_marks_missing_performance_unknown_and_batches_info(session):
    db_session, engine = session
    _, employees = await _add_department_and_employees(db_session, count=2)
    await db_session.commit()

    select_count = 0

    def count_selects(_conn, _cursor, statement, _parameters, _context, _executemany):
        nonlocal select_count
        if statement.lstrip().upper().startswith("SELECT"):
            select_count += 1

    event.listen(engine.sync_engine, "before_cursor_execute", count_selects)
    result = await evaluate_promotion_readiness(db_session)
    event.remove(engine.sync_engine, "before_cursor_execute", count_selects)

    assert len(result.items) == len(employees)
    assert {item.latest_rating for item in result.items} == {"未知"}
    assert {item.readiness_score for item in result.items} == {25}
    assert select_count == 6


async def test_candidate_score_is_deduplicated_normalized_and_keeps_unknown_performance(session):
    db_session, _ = session
    _, (employee,) = await _add_department_and_employees(db_session)
    today = date.today()
    db_session.add_all([
        Skill(employee_id=employee.id, name="Python", category="技术", level="高级", source="上级评", verified=True),
        Skill(employee_id=employee.id, name="Python", category="技术", level="专家", source="认证", verified=True),
        ProjectExperience(
            employee_id=employee.id, project_name="Python 平台", role="负责人",
            start_date=today - timedelta(days=100), end_date=None,
            description="Python 服务", achievement="上线",
        ),
        ProjectExperience(
            employee_id=employee.id, project_name="Python 工具", role="参与者",
            start_date=today - timedelta(days=200), end_date=today - timedelta(days=150),
            description="Python 工具", achievement="交付",
        ),
        Training(
            employee_id=employee.id, course_name="Python 进阶", category="专业技能",
            hours=Decimal("8"), score=90, status="已完成", provider="内训",
            assigned_by="", deadline=today, completed_date=today,
        ),
        Training(
            employee_id=employee.id, course_name="Python 实战", category="专业技能",
            hours=Decimal("8"), score=90, status="已完成", provider="内训",
            assigned_by="", deadline=today, completed_date=today,
        ),
    ])
    await db_session.commit()

    result = await find_candidates(db_session, "python, Python, python")

    assert result.total == 1
    candidate = result.candidates[0]
    assert candidate.match_score == 100
    assert candidate.latest_rating == "未知"
    assert candidate.matched_skills == ["Python(专家)"]
    assert candidate.relevant_projects == ["Python 平台"]


async def test_training_completion_rate_uses_training_records_as_denominator(session):
    db_session, _ = session
    _, (employee,) = await _add_department_and_employees(db_session)
    today = date.today()
    for index, status in enumerate(["已完成", "已完成", "进行中"]):
        db_session.add(Training(
            employee_id=employee.id, course_name=f"课程{index}", category="合规必修",
            hours=Decimal("2"), score=None, status=status, provider="内训",
            assigned_by="HR", deadline=today,
            completed_date=today if status == "已完成" else None,
        ))
    await db_session.commit()

    (summary,) = await get_training_summary(db_session, today.year)

    assert summary.completed_count == 2
    assert summary.completion_rate == 0.67
    assert summary.mandatory_completion_rate == 0.67


async def test_transfer_and_turnover_use_historical_departments_and_bounded_period(session):
    db_session, _ = session
    department_a = Department(name="A部门", parent_id=None, manager_id=None)
    department_b = Department(name="B部门", parent_id=None, manager_id=None)
    db_session.add_all([department_a, department_b])
    await db_session.flush()
    today = date.today()

    active = Employee(
        name="调岗员工", employee_no="MOVE01", department_id=department_b.id,
        position="工程师", level="P7", hire_date=today - timedelta(days=800),
        status="在职", email="", phone="",
    )
    resigned = Employee(
        name="近期离职", employee_no="LEFT01", department_id=department_b.id,
        position="工程师", level="P6", hire_date=today - timedelta(days=800),
        status="离职", email="", phone="",
    )
    old_resigned = Employee(
        name="早期离职", employee_no="LEFT02", department_id=department_a.id,
        position="工程师", level="P6", hire_date=today - timedelta(days=1200),
        status="离职", email="", phone="",
    )
    db_session.add_all([active, resigned, old_resigned])
    await db_session.flush()

    year = today.year
    db_session.add_all([
        EmploymentHistory(
            employee_id=active.id, start_date=date(year - 1, 1, 1),
            end_date=date(year, 1, 31), department="A部门", position="工程师",
            level="P6", change_type="入职", remark="",
        ),
        EmploymentHistory(
            employee_id=active.id, start_date=date(year, 2, 1), end_date=None,
            department="B部门", position="高级工程师", level="P7",
            change_type="调岗", remark="",
        ),
        EmploymentHistory(
            employee_id=resigned.id, start_date=today - timedelta(days=700),
            end_date=today - timedelta(days=30), department="A部门", position="工程师",
            level="P6", change_type="入职", remark="",
        ),
        EmploymentHistory(
            employee_id=old_resigned.id, start_date=today - timedelta(days=1100),
            end_date=today - timedelta(days=500), department="A部门", position="工程师",
            level="P6", change_type="入职", remark="",
        ),
    ])
    await db_session.commit()

    promotion = {r.department_name: r for r in await get_promotion_stats(db_session, year)}
    turnover = {r.department_name: r for r in await get_turnover_analysis(db_session)}

    assert promotion["A部门"].transfer_out_count == 1
    assert promotion["B部门"].transfer_in_count == 1
    assert turnover["A部门"].resigned_count == 1
    assert turnover["A部门"].total_count == 1
    assert turnover["A部门"].avg_tenure_years < 3
