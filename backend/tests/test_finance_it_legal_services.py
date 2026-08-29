"""财务、IT、法务关键状态机回归测试。"""

import asyncio
import json
import threading
from datetime import date
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.exceptions import BusinessException, ExternalServiceException
from app.models.base import Base
from app.models.finance import Budget, BudgetUsage, Reimbursement
from app.models.hr import Department, Employee
from app.models.it import ITAsset, ITTicket
from app.models.legal import Contract
from app.services import finance, it, legal
from app.tools.finance.admin_action import fin_admin_process_invoice_request


@pytest_asyncio.fixture
async def session_factory(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'services.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


async def _seed_people(session_factory):
    async with session_factory() as session:
        department = Department(name="研发部")
        session.add(department)
        await session.flush()
        applicant = Employee(
            name="申请人", employee_no="E001", department_id=department.id,
            status="在职",
        )
        reviewer = Employee(
            name="审核人", employee_no="E002", department_id=department.id,
            status="在职",
        )
        former_employee = Employee(
            name="离职员工", employee_no="E003", department_id=department.id,
            status="离职",
        )
        session.add_all([applicant, reviewer, former_employee])
        await session.commit()
        return department.id, applicant.id, reviewer.id, former_employee.id


async def _seed_reimbursement(session_factory, *, budget_status="active", available=1000.0):
    department_id, applicant_id, reviewer_id, _ = await _seed_people(session_factory)
    async with session_factory() as session:
        budget = Budget(
            department_id=department_id,
            year=date.today().year,
            total_amount=available,
            used_amount=0,
            status=budget_status,
        )
        reimbursement = Reimbursement(
            reimbursement_no="FIN-001",
            employee_id=applicant_id,
            department_id=department_id,
            type="差旅",
            amount=100,
            status="pending",
        )
        session.add_all([budget, reimbursement])
        await session.commit()
        return reimbursement.id, reviewer_id, budget.id


@pytest.mark.asyncio
async def test_reimbursement_concurrent_review_only_records_budget_once(session_factory):
    reimbursement_id, reviewer_id, budget_id = await _seed_reimbursement(session_factory)

    async def approve():
        async with session_factory() as session:
            try:
                await finance.review_reimbursement(
                    session, reimbursement_id, reviewer_id, "approve", "同意",
                )
                await session.commit()
                return True
            except BusinessException:
                await session.rollback()
                return False

    results = await asyncio.gather(approve(), approve())
    assert sorted(results) == [False, True]

    async with session_factory() as session:
        budget = await session.get(Budget, budget_id)
        usage_count = await session.scalar(
            select(func.count()).select_from(BudgetUsage).where(
                BudgetUsage.reimbursement_id == reimbursement_id,
            ),
        )
        assert budget.used_amount == 100
        assert usage_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("budget_status", "available", "message"),
    [("frozen", 1000, "预算当前不可用"), ("active", 50, "预算余额不足")],
)
async def test_reimbursement_rejects_unavailable_budget(
    session_factory, budget_status, available, message,
):
    reimbursement_id, reviewer_id, _ = await _seed_reimbursement(
        session_factory, budget_status=budget_status, available=available,
    )
    async with session_factory() as session:
        with pytest.raises(BusinessException) as exc_info:
            await finance.review_reimbursement(
                session, reimbursement_id, reviewer_id, "approve",
            )
        assert message in exc_info.value.message
        await session.rollback()
        reimbursement = await session.get(Reimbursement, reimbursement_id)
        assert reimbursement.status == "pending"


@pytest.mark.asyncio
async def test_ticket_state_machine_requires_accept_and_resolution(session_factory):
    _, applicant_id, reviewer_id, _ = await _seed_people(session_factory)
    async with session_factory() as session:
        ticket = ITTicket(
            ticket_no="IT-T-STATE", type="repair", title="电脑故障",
            status="open", priority="high", submitter_id=applicant_id,
        )
        session.add(ticket)
        await session.commit()

        with pytest.raises(BusinessException) as exc_info:
            await it.handle_ticket(session, ticket.id, reviewer_id, "resolve", "已修复")
        assert "不允许执行" in exc_info.value.message
        await it.handle_ticket(session, ticket.id, reviewer_id, "accept")
        with pytest.raises(BusinessException) as exc_info:
            await it.handle_ticket(session, ticket.id, reviewer_id, "resolve", "  ")
        assert "必须填写" in exc_info.value.message
        resolved = await it.handle_ticket(session, ticket.id, reviewer_id, "resolve", "已更换硬盘")
        assert resolved.status == "resolved"
        assert resolved.resolution == "已更换硬盘"
        closed = await it.handle_ticket(session, ticket.id, reviewer_id, "close")
        assert closed.status == "closed"


@pytest.mark.asyncio
async def test_asset_cannot_be_assigned_to_former_employee(session_factory):
    _, _, reviewer_id, former_employee_id = await _seed_people(session_factory)
    async with session_factory() as session:
        asset = ITAsset(asset_no="IT-A-001", type="laptop", status="idle")
        session.add(asset)
        await session.commit()

        with pytest.raises(BusinessException) as exc_info:
            await it.assign_asset(session, asset.id, former_employee_id, reviewer_id)
        assert "在职员工" in exc_info.value.message
        await session.refresh(asset)
        assert asset.status == "idle"
        assert asset.employee_id is None


@pytest.mark.asyncio
async def test_concurrent_ticket_numbers_are_unique(session_factory):
    _, applicant_id, _, _ = await _seed_people(session_factory)

    async def create(index):
        async with session_factory() as session:
            ticket = await it.create_ticket(
                session, applicant_id, "other", f"问题 {index}",
            )
            await session.commit()
            return ticket.ticket_no

    numbers = await asyncio.gather(*(create(index) for index in range(5)))
    assert len(set(numbers)) == len(numbers)
    assert all(number.startswith("IT-T-") for number in numbers)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("ticket_type", "title", "priority", "message"),
    [
        ("unknown", "问题", "medium", "工单类型"),
        ("other", "   ", "medium", "标题不能为空"),
        ("other", "问题", "critical", "优先级"),
    ],
)
async def test_create_ticket_validates_business_fields(
    session_factory, ticket_type, title, priority, message,
):
    _, applicant_id, _, _ = await _seed_people(session_factory)
    async with session_factory() as session:
        with pytest.raises(BusinessException, match=message):
            await it.create_ticket(session, applicant_id, ticket_type, title, priority=priority)


async def _seed_contract(session_factory):
    department_id, applicant_id, _, _ = await _seed_people(session_factory)
    async with session_factory() as session:
        contract = Contract(
            contract_no="LEG-001", title="采购合同", type="采购",
            party_a="甲方", party_b="乙方", amount=1000,
            start_date=date.today(), end_date=date.today(), status="pending",
            content="采购设备", key_terms="付款后交付",
            submitted_by=applicant_id, department_id=department_id,
        )
        session.add(contract)
        await session.commit()
        return contract.id


@pytest.mark.asyncio
async def test_contract_analysis_runs_model_off_event_loop(session_factory, monkeypatch):
    contract_id = await _seed_contract(session_factory)
    event_loop_thread = threading.get_ident()
    invoked_threads = []

    class Model:
        def invoke(self, _prompt):
            invoked_threads.append(threading.get_ident())
            return SimpleNamespace(content=json.dumps({
                "summary": "摘要", "risks": ["风险"], "suggestions": ["建议"],
            }))

    monkeypatch.setattr(legal, "get_model", lambda: Model())
    async with session_factory() as session:
        result = await legal.analyze_contract(session, contract_id)

    assert result.summary == "摘要"
    assert invoked_threads and invoked_threads[0] != event_loop_thread


@pytest.mark.asyncio
async def test_contract_analysis_rejects_malformed_structure(session_factory, monkeypatch):
    contract_id = await _seed_contract(session_factory)
    model = SimpleNamespace(invoke=lambda _prompt: SimpleNamespace(
        content='{"summary": "摘要", "risks": "不是列表", "suggestions": []}',
    ))
    monkeypatch.setattr(legal, "get_model", lambda: model)

    async with session_factory() as session:
        with pytest.raises(ExternalServiceException) as exc_info:
            await legal.analyze_contract(session, contract_id)
        assert "返回格式异常" in exc_info.value.message


@pytest.mark.asyncio
async def test_invoice_tool_only_prepares_user_action(monkeypatch):
    monkeypatch.setattr(
        "app.tools.finance.admin_action.get_finance_id", lambda _context: 1,
    )
    result = json.loads(await fin_admin_process_invoice_request(
        None, "测试客户", 88.5, "服务费",
    ))
    assert result["status"] == "prepared"
    assert result["requires_user_action"] is True
    assert "已开具" not in result["message"]
