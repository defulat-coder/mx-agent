"""数据库约束与 SQLite 外键开关测试。"""

from datetime import date
from decimal import Decimal
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import _enable_sqlite_foreign_keys
from app.models.admin import OfficeSupply
from app.models.base import Base
from app.models.finance import Budget, BudgetUsage, Reimbursement
from app.models.hr import AttendanceRecord, Department, Employee


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    event.listen(test_engine.sync_engine, "connect", _enable_sqlite_foreign_keys)
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await test_engine.dispose()


async def _seed_employee(session: AsyncSession) -> tuple[int, int]:
    department = Department(name="技术部")
    session.add(department)
    await session.flush()
    employee = Employee(name="张三", employee_no="MX0001", department_id=department.id)
    session.add(employee)
    await session.commit()
    return department.id, employee.id


def test_high_value_constraints_are_registered() -> None:
    constraint_names = {
        constraint.name
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if constraint.name
    }
    assert {
        "uq_leave_balance_employee_year_type",
        "uq_salary_employee_month",
        "uq_social_insurance_employee_month",
        "uq_attendance_employee_date",
        "uq_budget_department_year",
        "uq_budget_usage_reimbursement",
        "uq_performance_employee_year_half",
        "uq_talent_review_employee_year",
        "uq_office_supply_name",
        "ck_budget_amounts_valid",
        "ck_office_supply_stock_non_negative",
        "ck_performance_score_range",
    } <= constraint_names


@pytest.mark.asyncio
async def test_sqlite_enforces_foreign_keys(db_session: AsyncSession) -> None:
    assert await db_session.scalar(text("PRAGMA foreign_keys")) == 1

    db_session.add(AttendanceRecord(employee_id=999, date=date(2026, 1, 1)))
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_natural_keys_reject_duplicates(db_session: AsyncSession) -> None:
    department_id, employee_id = await _seed_employee(db_session)

    db_session.add(AttendanceRecord(employee_id=employee_id, date=date(2026, 1, 1)))
    await db_session.commit()
    db_session.add(AttendanceRecord(employee_id=employee_id, date=date(2026, 1, 1)))
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    db_session.add(Budget(
        department_id=department_id,
        year=2026,
        total_amount=Decimal("1000.00"),
        used_amount=Decimal("100.00"),
    ))
    await db_session.commit()
    db_session.add(Budget(
        department_id=department_id,
        year=2026,
        total_amount=Decimal("2000.00"),
    ))
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_checks_and_reimbursement_usage_idempotency(db_session: AsyncSession) -> None:
    department_id, employee_id = await _seed_employee(db_session)

    db_session.add(OfficeSupply(name="A4 纸", category="耗材", stock=-1, unit="包"))
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    budget = Budget(
        department_id=department_id,
        year=2026,
        total_amount=Decimal("1000.00"),
    )
    reimbursement = Reimbursement(
        reimbursement_no="FIN-R-0001",
        employee_id=employee_id,
        type="办公",
        amount=Decimal("100.00"),
        department_id=department_id,
    )
    db_session.add_all([budget, reimbursement])
    await db_session.commit()

    db_session.add(BudgetUsage(
        budget_id=budget.id,
        reimbursement_id=reimbursement.id,
        amount=Decimal("100.00"),
        category="办公",
        used_date=date(2026, 1, 1),
    ))
    await db_session.commit()
    db_session.add(BudgetUsage(
        budget_id=budget.id,
        reimbursement_id=reimbursement.id,
        amount=Decimal("100.00"),
        category="办公",
        used_date=date(2026, 1, 2),
    ))
    with pytest.raises(IntegrityError):
        await db_session.commit()
