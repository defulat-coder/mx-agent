"""行政业务状态机与输入边界测试。"""

import json
from datetime import datetime, time, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.exceptions import BusinessException
from app.models.admin import MeetingRoom, OfficeSupply, RoomBooking, SupplyRequest, Visitor
from app.models.base import Base
from app.models.hr import Employee
from app.services import admin as admin_service
from app.tools.admin.action import adm_apply_travel


@pytest_asyncio.fixture
async def admin_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    tables = [
        Employee.__table__,
        MeetingRoom.__table__,
        OfficeSupply.__table__,
        RoomBooking.__table__,
        SupplyRequest.__table__,
        Visitor.__table__,
    ]
    async with engine.begin() as connection:
        await connection.run_sync(lambda sync_connection: Base.metadata.create_all(sync_connection, tables=tables))
    async with factory.begin() as session:
        session.add_all([
            Employee(id=1, name="员工", employee_no="MX0001", status="在职"),
            Employee(id=2, name="行政", employee_no="MX0002", status="在职"),
            MeetingRoom(id=1, name="海棠", floor="3F", capacity=8, status="available"),
            OfficeSupply(id=1, name="A4纸", category="耗材", stock=10, unit="包"),
            OfficeSupply(id=2, name="签字笔", category="文具", stock=3, unit="支"),
        ])
    yield factory
    await engine.dispose()


def _tomorrow_at(hour: int, minute: int = 0) -> datetime:
    tomorrow = datetime.now(admin_service.LOCAL_TIMEZONE).date() + timedelta(days=1)
    return datetime.combine(tomorrow, time(hour, minute))


async def test_book_room_normalizes_timezone_and_rejects_conflict(admin_db):
    local_start = _tomorrow_at(9)
    utc_start = local_start.replace(tzinfo=admin_service.LOCAL_TIMEZONE).astimezone(timezone.utc)
    utc_end = utc_start + timedelta(hours=1)

    async with admin_db() as session, session.begin():
        booking = await admin_service.book_room(session, 1, 1, " 周会 ", utc_start, utc_end)
    assert booking.start_time == local_start
    assert booking.start_time.tzinfo is None
    assert booking.title == "周会"

    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.book_room(
                session, 1, 1, "冲突会议", local_start + timedelta(minutes=30), local_start + timedelta(hours=1),
            )
    assert "已有其他会议" in exc_info.value.message


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (lambda: datetime.now(admin_service.LOCAL_TIMEZONE) - timedelta(hours=1),
         lambda: datetime.now(admin_service.LOCAL_TIMEZONE), "过去"),
        (lambda: _tomorrow_at(9), lambda: _tomorrow_at(13, 30), "最长 4 小时"),
        (lambda: _tomorrow_at(9, 15), lambda: _tomorrow_at(10), "30 分钟整点"),
    ],
)
async def test_book_room_rejects_invalid_time_range(admin_db, start, end, message):
    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.book_room(session, 1, 1, "会议", start(), end())
    assert message in exc_info.value.message


@pytest.mark.parametrize(
    "items",
    [
        "not-json",
        "[]",
        '[{"name":"A4纸","quantity":0}]',
        '[{"name":"A4纸","quantity":true}]',
        '[{"name":"不存在","quantity":1}]',
    ],
)
async def test_request_supply_rejects_invalid_items(admin_db, items):
    with pytest.raises(BusinessException):
        async with admin_db() as session, session.begin():
            await admin_service.request_supply(session, 1, items)


async def test_supply_approval_batches_items_and_cannot_run_twice(admin_db):
    items = '[{"name":"A4纸","quantity":2},{"name":"A4纸","quantity":1},{"name":"签字笔","quantity":2}]'
    async with admin_db() as session, session.begin():
        request = await admin_service.request_supply(session, 1, items)
    assert json.loads(request.items) == [
        {"name": "A4纸", "quantity": 3},
        {"name": "签字笔", "quantity": 2},
    ]

    async with admin_db() as session, session.begin():
        approved = await admin_service.approve_supply(session, request.request_id, 2, "approve", "同意")
    assert approved.status == "approved"

    async with admin_db() as session:
        stocks = dict((await session.execute(select(OfficeSupply.name, OfficeSupply.stock))).all())
    assert stocks == {"A4纸": 7, "签字笔": 1}

    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.approve_supply(session, request.request_id, 2, "approve")
    assert "已处理" in exc_info.value.message


async def test_supply_approval_rolls_back_when_stock_is_insufficient(admin_db):
    async with admin_db() as session, session.begin():
        request = await admin_service.request_supply(session, 1, '[{"name":"签字笔","quantity":4}]')

    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.approve_supply(session, request.request_id, 2, "approve")
    assert "库存不足" in exc_info.value.message

    async with admin_db() as session:
        stock = await session.scalar(select(OfficeSupply.stock).where(OfficeSupply.name == "签字笔"))
        status = await session.scalar(select(SupplyRequest.status).where(SupplyRequest.id == request.request_id))
    assert stock == 3
    assert status == "pending"


async def test_supply_approval_rejects_corrupt_legacy_json(admin_db):
    async with admin_db() as session, session.begin():
        request = SupplyRequest(employee_id=1, items="invalid", status="pending")
        session.add(request)
        await session.flush()
        request_id = request.id

    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.approve_supply(session, request_id, 2, "approve")
    assert "有效的 JSON" in exc_info.value.message


async def test_visitor_rejects_past_date_and_invalid_time(admin_db):
    yesterday = datetime.now(admin_service.LOCAL_TIMEZONE).date() - timedelta(days=1)
    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.book_visitor(session, 1, "访客", visit_date=yesterday.isoformat())
    assert "不能早于今天" in exc_info.value.message

    tomorrow = _tomorrow_at(9).date().isoformat()
    with pytest.raises(BusinessException) as exc_info:
        async with admin_db() as session, session.begin():
            await admin_service.book_visitor(
                session, 1, "访客", visit_date=tomorrow, visit_time="10:00-09:00",
            )
    assert "结束时间" in exc_info.value.message


async def test_travel_action_is_prepared_not_submitted():
    tomorrow = _tomorrow_at(9).date()
    context = SimpleNamespace(session_id="test", session_state={"employee_id": 1})
    result = json.loads(await adm_apply_travel(
        context, "上海 & 苏州", tomorrow.isoformat(), (tomorrow + timedelta(days=1)).isoformat(), "客户拜访",
    ))

    assert result["status"] == "prepared"
    assert result["requires_user_action"] is True
    assert "确认并提交" in result["message"]
    assert parse_qs(urlparse(result["approval_url"]).query)["dest"] == ["上海 & 苏州"]
