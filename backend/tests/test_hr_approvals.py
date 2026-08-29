"""HR 审批状态机回归测试。"""

import asyncio
from datetime import date, time
from decimal import Decimal

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.hr import Department, Employee, LeaveBalance, LeaveRequest, OvertimeRecord
from app.services.hr.admin import admin_approve_leave_request, admin_approve_overtime_request
from app.services.hr.manager import approve_leave_request, approve_overtime_request


@pytest_asyncio.fixture
async def session_factory(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'hr-approvals.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    current_year = date.today().year
    async with factory.begin() as session:
        engineering = Department(id=1, name="研发部")
        other = Department(id=2, name="其他部")
        session.add_all([engineering, other])
        await session.flush()
        session.add_all([
            Employee(id=1, name="主管", employee_no="M1", department_id=1),
            Employee(id=2, name="下属", employee_no="E2", department_id=1),
            Employee(id=3, name="外部员工", employee_no="E3", department_id=2),
            Employee(id=4, name="管理员", employee_no="A4", department_id=2),
        ])
        await session.flush()
        engineering.manager_id = 1
        other.manager_id = 4
        session.add_all([
            LeaveBalance(
                employee_id=2, year=current_year, leave_type="年假",
                total_days=Decimal("10"), used_days=Decimal("1"), remaining_days=Decimal("9"),
            ),
            LeaveBalance(
                employee_id=3, year=current_year, leave_type="年假",
                total_days=Decimal("10"), used_days=Decimal("0"), remaining_days=Decimal("10"),
            ),
            LeaveBalance(
                employee_id=4, year=current_year, leave_type="年假",
                total_days=Decimal("10"), used_days=Decimal("0"), remaining_days=Decimal("10"),
            ),
            LeaveRequest(
                id=1, employee_id=2, leave_type="年假", start_date=date(current_year, 2, 1),
                end_date=date(current_year, 2, 2), days=Decimal("2"), reason="休息",
            ),
            LeaveRequest(
                id=2, employee_id=1, leave_type="年假", start_date=date(current_year, 2, 1),
                end_date=date(current_year, 2, 1), days=Decimal("1"), reason="自批测试",
            ),
            LeaveRequest(
                id=3, employee_id=3, leave_type="年假", start_date=date(current_year, 2, 1),
                end_date=date(current_year, 2, 1), days=Decimal("1"), reason="范围测试",
            ),
            LeaveRequest(
                id=4, employee_id=2, leave_type="年假", start_date=date(current_year, 3, 1),
                end_date=date(current_year, 3, 20), days=Decimal("20"), reason="余额测试",
            ),
            LeaveRequest(
                id=5, employee_id=4, leave_type="年假", start_date=date(current_year, 4, 1),
                end_date=date(current_year, 4, 1), days=Decimal("1"), reason="管理员自批测试",
            ),
            LeaveRequest(
                id=6, employee_id=2, leave_type="病假", start_date=date(current_year, 5, 1),
                end_date=date(current_year, 5, 1), days=Decimal("1"), reason="拒绝测试",
            ),
            OvertimeRecord(
                id=1, employee_id=2, date=date(current_year, 2, 1),
                start_time=time(18), end_time=time(20), hours=Decimal("2"), type="工作日",
            ),
            OvertimeRecord(
                id=2, employee_id=1, date=date(current_year, 2, 1),
                start_time=time(18), end_time=time(19), hours=Decimal("1"), type="工作日",
            ),
            OvertimeRecord(
                id=3, employee_id=3, date=date(current_year, 2, 1),
                start_time=time(18), end_time=time(19), hours=Decimal("1"), type="工作日",
            ),
            OvertimeRecord(
                id=4, employee_id=4, date=date(current_year, 2, 1),
                start_time=time(18), end_time=time(19), hours=Decimal("1"), type="工作日",
            ),
        ])

    yield factory
    await engine.dispose()


async def test_leave_approval_is_single_use_and_deducts_balance_once(session_factory):
    async def approve_once():
        async with session_factory() as session, session.begin():
            return await admin_approve_leave_request(session, 4, 1, "通过", "同意")

    results = await asyncio.gather(approve_once(), approve_once())
    assert sorted(result.success for result in results) == [False, True]
    assert "暂不保存审批备注" in next(result.message for result in results if result.success)

    async with session_factory() as session:
        request = await session.get(LeaveRequest, 1)
        balance = await session.scalar(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == 2,
                LeaveBalance.year == date.today().year,
                LeaveBalance.leave_type == "年假",
            )
        )
        assert request.status == "已通过"
        assert balance.used_days == Decimal("3.0")
        assert balance.remaining_days == Decimal("7.0")


async def test_rejection_does_not_require_or_deduct_balance(session_factory):
    async with session_factory() as session, session.begin():
        result = await approve_leave_request(session, 1, 1, 6, "拒绝", "材料不足")

    assert result.success is True
    async with session_factory() as session:
        request = await session.get(LeaveRequest, 6)
        balance = await session.scalar(
            select(LeaveBalance).where(LeaveBalance.employee_id == 2, LeaveBalance.leave_type == "年假")
        )
        assert request.status == "已拒绝"
        assert balance.used_days == Decimal("1.0")
        assert balance.remaining_days == Decimal("9.0")


async def test_insufficient_balance_keeps_request_pending(session_factory):
    async with session_factory() as session, session.begin():
        result = await approve_leave_request(session, 1, 1, 4, "通过")

    assert result.success is False
    assert result.message == "假期余额不足"
    async with session_factory() as session:
        request = await session.get(LeaveRequest, 4)
        balance = await session.scalar(
            select(LeaveBalance).where(LeaveBalance.employee_id == 2, LeaveBalance.leave_type == "年假")
        )
        assert request.status == "待审批"
        assert balance.remaining_days == Decimal("9.0")


async def test_manager_cannot_self_approve_or_approve_outside_scope(session_factory):
    async with session_factory() as session, session.begin():
        self_result = await approve_leave_request(session, 1, 1, 2, "拒绝")
        outside_result = await approve_overtime_request(session, 1, 1, 3, "通过")

    assert self_result.success is False
    assert self_result.message == "不能审批自己的请假申请"
    assert outside_result.success is False
    assert "不在您的管辖范围" in outside_result.message


async def test_admin_cannot_self_approve(session_factory):
    async with session_factory() as session, session.begin():
        leave_result = await admin_approve_leave_request(session, 4, 5, "通过")
        overtime_result = await admin_approve_overtime_request(session, 4, 4, "拒绝")

    assert leave_result.success is False
    assert overtime_result.success is False
    assert "不能审批自己的" in leave_result.message
    assert "不能审批自己的" in overtime_result.message


async def test_invalid_action_never_changes_status(session_factory):
    async with session_factory() as session, session.begin():
        leave_result = await approve_leave_request(session, 1, 1, 1, "驳回")
        overtime_result = await approve_overtime_request(session, 1, 1, 1, "批准")

    assert leave_result.success is False
    assert overtime_result.success is False
    async with session_factory() as session:
        assert (await session.get(LeaveRequest, 1)).status == "待审批"
        assert (await session.get(OvertimeRecord, 1)).status == "待审批"


async def test_service_does_not_commit_its_own_transaction(session_factory):
    async with session_factory() as session:
        result = await admin_approve_overtime_request(session, 4, 1, "拒绝")
        assert result.success is True

    async with session_factory() as session:
        assert (await session.get(OvertimeRecord, 1)).status == "待审批"
