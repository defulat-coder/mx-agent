"""行政管理 Service — 会议室、办公用品、快递、访客、差旅"""

import json
from datetime import datetime, timedelta, timezone

from loguru import logger
from sqlalchemy import Date, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, NotFoundException
from app.models.admin import Express, MeetingRoom, OfficeSupply, RoomBooking, SupplyRequest, Visitor
from app.models.hr import Employee
from app.schemas.admin import (
    ExpressResponse,
    MeetingRoomResponse,
    OfficeSupplyResponse,
    RoomBookingResponse,
    RoomUsageStatsResponse,
    SupplyRequestResponse,
    SupplyStatsResponse,
    VisitorResponse,
)


# ── 会议室查询 ─────────────────────────────────────────────


def _room_to_response(r: MeetingRoom) -> MeetingRoomResponse:
    return MeetingRoomResponse(
        room_id=r.id, name=r.name, floor=r.floor,
        capacity=r.capacity, equipment=r.equipment, status=r.status,
    )


async def get_available_rooms(
    session: AsyncSession,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[MeetingRoomResponse]:
    """查询可用会议室，指定时间段则排除有冲突的。"""
    logger.info("查询可用会议室 | start={s} end={e}", s=start_time, e=end_time)
    stmt = select(MeetingRoom).where(MeetingRoom.status == "available")
    if start_time and end_time:
        # 排除有冲突预订的会议室
        conflict = (
            select(RoomBooking.room_id)
            .where(
                RoomBooking.status == "active",
                RoomBooking.start_time < end_time,
                RoomBooking.end_time > start_time,
            )
        )
        stmt = stmt.where(MeetingRoom.id.notin_(conflict))
    rooms = (await session.execute(stmt.order_by(MeetingRoom.id))).scalars().all()
    return [_room_to_response(r) for r in rooms]


# ── 会议室预订 ─────────────────────────────────────────────


def _validate_slot(dt_val: datetime) -> None:
    """校验 30 分钟槽位对齐。"""
    if dt_val.minute not in (0, 30) or dt_val.second != 0:
        raise BusinessException(message=f"时间必须为 30 分钟整点（:00 或 :30），当前: {dt_val.strftime('%H:%M:%S')}")


async def book_room(
    session: AsyncSession,
    employee_id: int,
    room_id: int,
    title: str,
    start_time: datetime,
    end_time: datetime,
) -> RoomBookingResponse:
    """预订会议室。

    Args:
        employee_id: 预订人 ID
        room_id: 会议室 ID
        title: 会议主题
        start_time: 开始时间
        end_time: 结束时间
    """
    logger.info("预订会议室 | room_id={rid} employee_id={eid}", rid=room_id, eid=employee_id)
    _validate_slot(start_time)
    _validate_slot(end_time)
    if end_time <= start_time:
        raise BusinessException(message="结束时间必须晚于开始时间")
    now = datetime.now(timezone.utc)
    if start_time > now + timedelta(days=7):
        raise BusinessException(message="最多提前 7 天预订")

    room = (await session.execute(select(MeetingRoom).where(MeetingRoom.id == room_id))).scalar_one_or_none()
    if not room:
        raise NotFoundException(message="会议室不存在")
    if room.status != "available":
        raise BusinessException(message="会议室当前不可用")

    # 冲突检测
    conflict_stmt = select(func.count()).where(
        RoomBooking.room_id == room_id,
        RoomBooking.status == "active",
        RoomBooking.start_time < end_time,
        RoomBooking.end_time > start_time,
    )
    cnt = (await session.execute(conflict_stmt)).scalar() or 0
    if cnt > 0:
        raise BusinessException(message="该时间段已有其他会议预订，请选择其他时间")

    booking = RoomBooking(
        room_id=room_id, employee_id=employee_id, title=title,
        start_time=start_time, end_time=end_time, status="active",
    )
    session.add(booking)
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == employee_id))).scalar_one_or_none() or ""
    return RoomBookingResponse(
        booking_id=booking.id, room_id=room_id, room_name=room.name,
        employee_id=employee_id, employee_name=emp_name,
        title=title, start_time=start_time, end_time=end_time,
        status="active", created_at=booking.created_at,
    )


async def get_my_bookings(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[RoomBookingResponse]:
    """查询员工的预订记录。"""
    logger.info("查询我的预订 | employee_id={eid}", eid=employee_id)
    stmt = (
        select(RoomBooking, MeetingRoom.name.label("room_name"))
        .outerjoin(MeetingRoom, RoomBooking.room_id == MeetingRoom.id)
        .where(RoomBooking.employee_id == employee_id)
        .order_by(RoomBooking.start_time.desc())
    )
    if status:
        stmt = stmt.where(RoomBooking.status == status)
    rows = (await session.execute(stmt)).all()
    return [
        RoomBookingResponse(
            booking_id=b.id, room_id=b.room_id, room_name=rn or "",
            employee_id=b.employee_id, employee_name="",
            title=b.title, start_time=b.start_time, end_time=b.end_time,
            status=b.status, created_at=b.created_at,
        )
        for b, rn in rows
    ]


async def cancel_booking(session: AsyncSession, booking_id: int, employee_id: int) -> RoomBookingResponse:
    """取消预订，仅限开始前 30 分钟。"""
    logger.info("取消预订 | booking_id={bid}", bid=booking_id)
    booking = (await session.execute(select(RoomBooking).where(RoomBooking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise NotFoundException(message="预订不存在")
    if booking.employee_id != employee_id:
        raise BusinessException(message="只能取消自己的预订")
    if booking.status != "active":
        raise BusinessException(message="预订已取消或已完成")
    now = datetime.now(timezone.utc)
    if booking.start_time <= now + timedelta(minutes=30):
        raise BusinessException(message="开始前 30 分钟内不可取消")

    booking.status = "cancelled"
    await session.flush()

    room_name = (await session.execute(select(MeetingRoom.name).where(MeetingRoom.id == booking.room_id))).scalar_one_or_none() or ""
    return RoomBookingResponse(
        booking_id=booking.id, room_id=booking.room_id, room_name=room_name,
        employee_id=booking.employee_id, employee_name="",
        title=booking.title, start_time=booking.start_time, end_time=booking.end_time,
        status="cancelled", created_at=booking.created_at,
    )


# ── 办公用品 ───────────────────────────────────────────────


async def request_supply(
    session: AsyncSession, employee_id: int, items: str,
) -> SupplyRequestResponse:
    """申领办公用品。

    Args:
        employee_id: 申请人 ID
        items: JSON 格式 [{name, quantity}]
    """
    logger.info("申领办公用品 | employee_id={eid}", eid=employee_id)
    req = SupplyRequest(employee_id=employee_id, items=items, status="pending")
    session.add(req)
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == employee_id))).scalar_one_or_none() or ""
    return SupplyRequestResponse(
        request_id=req.id, employee_id=employee_id, employee_name=emp_name,
        items=items, status="pending", created_at=req.created_at,
    )


async def get_supply_requests(
    session: AsyncSession, status: str | None = None,
) -> list[SupplyRequestResponse]:
    """查询申领单（行政人员）。"""
    logger.info("查询申领单 | status={s}", s=status or "全部")
    stmt = (
        select(SupplyRequest, Employee.name.label("emp_name"))
        .outerjoin(Employee, SupplyRequest.employee_id == Employee.id)
        .order_by(SupplyRequest.created_at.desc())
    )
    if status:
        stmt = stmt.where(SupplyRequest.status == status)
    rows = (await session.execute(stmt)).all()
    return [
        SupplyRequestResponse(
            request_id=r.id, employee_id=r.employee_id, employee_name=en or "",
            items=r.items, status=r.status, approved_by=r.approved_by,
            remark=r.remark, created_at=r.created_at,
        )
        for r, en in rows
    ]


async def get_supply_stock(
    session: AsyncSession, category: str | None = None,
) -> list[OfficeSupplyResponse]:
    """查询库存。"""
    logger.info("查询库存 | category={c}", c=category or "全部")
    stmt = select(OfficeSupply).order_by(OfficeSupply.category, OfficeSupply.name)
    if category:
        stmt = stmt.where(OfficeSupply.category == category)
    supplies = (await session.execute(stmt)).scalars().all()
    return [
        OfficeSupplyResponse(
            supply_id=s.id, name=s.name, category=s.category,
            stock=s.stock, unit=s.unit,
        )
        for s in supplies
    ]


async def approve_supply(
    session: AsyncSession, request_id: int, admin_id: int, action: str, remark: str = "",
) -> SupplyRequestResponse:
    """审批申领单。

    Args:
        request_id: 申领单 ID
        admin_id: 审批人 ID
        action: approve / reject
        remark: 备注
    """
    logger.info("审批申领单 | request_id={rid} action={act}", rid=request_id, act=action)
    req = (await session.execute(select(SupplyRequest).where(SupplyRequest.id == request_id))).scalar_one_or_none()
    if not req:
        raise NotFoundException(message="申领单不存在")
    if req.status != "pending":
        raise BusinessException(message="申领单已处理")

    if action == "approve":
        # 扣减库存
        try:
            item_list = json.loads(req.items) if req.items else []
        except json.JSONDecodeError:
            item_list = []
        for item in item_list:
            name = item.get("name", "")
            qty = item.get("quantity", 0)
            supply = (await session.execute(
                select(OfficeSupply).where(OfficeSupply.name == name),
            )).scalar_one_or_none()
            if supply and supply.stock < qty:
                raise BusinessException(message=f"'{name}' 库存不足（剩余 {supply.stock}，申请 {qty}）")
            if supply:
                supply.stock -= qty
        req.status = "approved"
    elif action == "reject":
        req.status = "rejected"
    else:
        raise BusinessException(message=f"不支持的操作: {action}")

    req.approved_by = admin_id
    req.remark = remark
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == req.employee_id))).scalar_one_or_none() or ""
    return SupplyRequestResponse(
        request_id=req.id, employee_id=req.employee_id, employee_name=emp_name,
        items=req.items, status=req.status, approved_by=req.approved_by,
        remark=req.remark, created_at=req.created_at,
    )


# ── 快递 ───────────────────────────────────────────────────


async def get_my_express(
    session: AsyncSession, employee_id: int, type: str | None = None,
) -> list[ExpressResponse]:
    """查询员工快递记录。"""
    logger.info("查询我的快递 | employee_id={eid} type={t}", eid=employee_id, t=type or "全部")
    stmt = select(Express).where(Express.employee_id == employee_id).order_by(Express.created_at.desc())
    if type:
        stmt = stmt.where(Express.type == type)
    records = (await session.execute(stmt)).scalars().all()
    return [
        ExpressResponse(
            express_id=e.id, tracking_no=e.tracking_no, type=e.type,
            employee_id=e.employee_id, courier=e.courier, status=e.status,
            received_at=e.received_at, remark=e.remark, created_at=e.created_at,
        )
        for e in records
    ]


async def get_all_express(
    session: AsyncSession, status: str | None = None, type: str | None = None,
) -> list[ExpressResponse]:
    """行政人员查询全部快递。"""
    logger.info("管理员查询快递 | status={s} type={t}", s=status or "全部", t=type or "全部")
    stmt = (
        select(Express, Employee.name.label("emp_name"))
        .outerjoin(Employee, Express.employee_id == Employee.id)
        .order_by(Express.created_at.desc())
    )
    if status:
        stmt = stmt.where(Express.status == status)
    if type:
        stmt = stmt.where(Express.type == type)
    rows = (await session.execute(stmt)).all()
    return [
        ExpressResponse(
            express_id=e.id, tracking_no=e.tracking_no, type=e.type,
            employee_id=e.employee_id, employee_name=en or "",
            courier=e.courier, status=e.status,
            received_at=e.received_at, remark=e.remark, created_at=e.created_at,
        )
        for e, en in rows
    ]


async def register_express(
    session: AsyncSession, tracking_no: str, type: str, employee_id: int, courier: str, remark: str = "",
) -> ExpressResponse:
    """行政人员登记快递。"""
    logger.info("登记快递 | tracking_no={tn} type={t}", tn=tracking_no, t=type)
    express = Express(
        tracking_no=tracking_no, type=type, employee_id=employee_id,
        courier=courier, status="pending", remark=remark,
    )
    session.add(express)
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == employee_id))).scalar_one_or_none() or ""
    return ExpressResponse(
        express_id=express.id, tracking_no=tracking_no, type=type,
        employee_id=employee_id, employee_name=emp_name,
        courier=courier, status="pending", remark=remark, created_at=express.created_at,
    )


# ── 访客 ───────────────────────────────────────────────────


async def get_my_visitors(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[VisitorResponse]:
    """查询员工的访客预约。"""
    logger.info("查询我的访客 | employee_id={eid}", eid=employee_id)
    stmt = select(Visitor).where(Visitor.host_id == employee_id).order_by(Visitor.visit_date.desc())
    if status:
        stmt = stmt.where(Visitor.status == status)
    records = (await session.execute(stmt)).scalars().all()
    return [
        VisitorResponse(
            visitor_id=v.id, visitor_name=v.visitor_name, company=v.company,
            phone=v.phone, host_id=v.host_id, visit_date=v.visit_date,
            visit_time=v.visit_time, purpose=v.purpose, status=v.status,
            created_at=v.created_at,
        )
        for v in records
    ]


async def book_visitor(
    session: AsyncSession,
    host_id: int,
    visitor_name: str,
    company: str = "",
    phone: str = "",
    visit_date: str = "",
    visit_time: str = "",
    purpose: str = "",
) -> VisitorResponse:
    """预约访客。"""
    logger.info("预约访客 | host_id={hid} visitor={vn}", hid=host_id, vn=visitor_name)
    from datetime import date as date_type
    vd = date_type.fromisoformat(visit_date)
    visitor = Visitor(
        visitor_name=visitor_name, company=company, phone=phone,
        host_id=host_id, visit_date=vd, visit_time=visit_time,
        purpose=purpose, status="pending",
    )
    session.add(visitor)
    await session.flush()

    host_name = (await session.execute(select(Employee.name).where(Employee.id == host_id))).scalar_one_or_none() or ""
    return VisitorResponse(
        visitor_id=visitor.id, visitor_name=visitor_name, company=company,
        phone=phone, host_id=host_id, host_name=host_name,
        visit_date=vd, visit_time=visit_time, purpose=purpose,
        status="pending", created_at=visitor.created_at,
    )


async def get_all_visitors(
    session: AsyncSession, date: str | None = None, status: str | None = None,
) -> list[VisitorResponse]:
    """行政人员查询访客。"""
    logger.info("管理员查询访客 | date={d} status={s}", d=date or "全部", s=status or "全部")
    stmt = (
        select(Visitor, Employee.name.label("host_name"))
        .outerjoin(Employee, Visitor.host_id == Employee.id)
        .order_by(Visitor.visit_date.desc())
    )
    if date:
        from datetime import date as date_type
        stmt = stmt.where(Visitor.visit_date == date_type.fromisoformat(date))
    if status:
        stmt = stmt.where(Visitor.status == status)
    rows = (await session.execute(stmt)).all()
    return [
        VisitorResponse(
            visitor_id=v.id, visitor_name=v.visitor_name, company=v.company,
            phone=v.phone, host_id=v.host_id, host_name=hn or "",
            visit_date=v.visit_date, visit_time=v.visit_time,
            purpose=v.purpose, status=v.status, created_at=v.created_at,
        )
        for v, hn in rows
    ]


# ── 行政管理员：会议室操作 ─────────────────────────────────


async def get_all_bookings(
    session: AsyncSession,
    room_id: int | None = None,
    status: str | None = None,
    date: str | None = None,
) -> list[RoomBookingResponse]:
    """行政人员查询全部预订。"""
    logger.info("管理员查询预订 | room_id={r} status={s} date={d}", r=room_id, s=status, d=date)
    stmt = (
        select(RoomBooking, MeetingRoom.name.label("room_name"), Employee.name.label("emp_name"))
        .outerjoin(MeetingRoom, RoomBooking.room_id == MeetingRoom.id)
        .outerjoin(Employee, RoomBooking.employee_id == Employee.id)
        .order_by(RoomBooking.start_time.desc())
    )
    if room_id:
        stmt = stmt.where(RoomBooking.room_id == room_id)
    if status:
        stmt = stmt.where(RoomBooking.status == status)
    if date:
        from datetime import date as date_type
        d = date_type.fromisoformat(date)
        stmt = stmt.where(func.date(RoomBooking.start_time) == d)
    rows = (await session.execute(stmt)).all()
    return [
        RoomBookingResponse(
            booking_id=b.id, room_id=b.room_id, room_name=rn or "",
            employee_id=b.employee_id, employee_name=en or "",
            title=b.title, start_time=b.start_time, end_time=b.end_time,
            status=b.status, created_at=b.created_at,
        )
        for b, rn, en in rows
    ]


async def release_room(
    session: AsyncSession, room_id: int, status: str,
) -> MeetingRoomResponse:
    """释放/维护会议室。"""
    logger.info("设置会议室状态 | room_id={rid} status={s}", rid=room_id, s=status)
    room = (await session.execute(select(MeetingRoom).where(MeetingRoom.id == room_id))).scalar_one_or_none()
    if not room:
        raise NotFoundException(message="会议室不存在")
    if status not in ("available", "maintenance"):
        raise BusinessException(message=f"不支持的状态: {status}")
    room.status = status
    await session.flush()
    return _room_to_response(room)


# ── 统计 ───────────────────────────────────────────────────


async def room_usage_stats(session: AsyncSession) -> RoomUsageStatsResponse:
    """会议室使用统计。"""
    logger.info("会议室使用统计")
    total_rooms = (await session.execute(select(func.count()).select_from(MeetingRoom))).scalar() or 0
    total_bookings = (await session.execute(
        select(func.count()).select_from(RoomBooking).where(RoomBooking.status == "active"),
    )).scalar() or 0
    by_room_stmt = (
        select(MeetingRoom.name, func.count().label("cnt"))
        .select_from(RoomBooking)
        .join(MeetingRoom, RoomBooking.room_id == MeetingRoom.id)
        .where(RoomBooking.status == "active")
        .group_by(MeetingRoom.name)
        .order_by(func.count().desc())
    )
    by_room = [{"room": name, "bookings": cnt} for name, cnt in (await session.execute(by_room_stmt)).all()]
    return RoomUsageStatsResponse(total_rooms=total_rooms, total_bookings=total_bookings, by_room=by_room)


async def supply_stats(session: AsyncSession) -> SupplyStatsResponse:
    """办公用品统计。"""
    logger.info("办公用品统计")
    total = (await session.execute(select(func.count()).select_from(SupplyRequest))).scalar() or 0
    status_stmt = select(SupplyRequest.status, func.count()).group_by(SupplyRequest.status)
    by_status = dict((await session.execute(status_stmt)).all())
    # 消耗 top5（简化：按申领次数）
    return SupplyStatsResponse(total_requests=total, by_status=by_status, top_items=[])
