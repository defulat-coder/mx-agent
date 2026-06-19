"""IT 运维 Service — 工单管理、设备资产管理、统计分析"""

from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, NotFoundException
from app.models.hr import Department, Employee
from app.models.it import ITAsset, ITAssetHistory, ITTicket
from app.schemas.it import (
    FaultTrendItem,
    ITAssetResponse,
    ITAssetStatsResponse,
    ITFaultTrendResponse,
    ITTicketResponse,
    ITTicketStatsResponse,
)


# ── 员工工单查询 ─────────────────────────────────────────────


async def get_my_tickets(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[ITTicketResponse]:
    """查询员工本人提交的工单列表。

    Args:
        employee_id: 当前员工 ID
        status: 可选状态筛选
    """
    logger.info("查询我的工单 | employee_id={eid} status={s}", eid=employee_id, s=status or "全部")
    stmt = (
        select(ITTicket, Employee.name.label("submitter_name"))
        .outerjoin(Employee, ITTicket.submitter_id == Employee.id)
        .where(ITTicket.submitter_id == employee_id)
        .order_by(ITTicket.created_at.desc())
    )
    if status:
        stmt = stmt.where(ITTicket.status == status)
    rows = (await session.execute(stmt)).all()
    return [
        ITTicketResponse(
            ticket_id=t.id,
            ticket_no=t.ticket_no,
            type=t.type,
            title=t.title,
            status=t.status,
            priority=t.priority,
            submitter_id=t.submitter_id,
            submitter_name=name or "",
            handler_id=t.handler_id,
            created_at=t.created_at,
        )
        for t, name in rows
    ]


async def get_ticket_detail(
    session: AsyncSession, ticket_id: int, employee_id: int | None = None,
) -> ITTicketResponse:
    """查询工单详情。

    Args:
        ticket_id: 工单 ID
        employee_id: 如非 None，校验是否为提交人（普通员工权限隔离）
    """
    logger.info("查询工单详情 | ticket_id={tid}", tid=ticket_id)
    stmt = select(ITTicket).where(ITTicket.id == ticket_id)
    ticket = (await session.execute(stmt)).scalar_one_or_none()
    if not ticket:
        raise NotFoundException(message="工单不存在")
    if employee_id is not None and ticket.submitter_id != employee_id:
        raise BusinessException(message="无权查看此工单")

    # 查提交人和处理人姓名
    submitter_name = ""
    handler_name = None
    ids = [ticket.submitter_id]
    if ticket.handler_id:
        ids.append(ticket.handler_id)
    names_stmt = select(Employee.id, Employee.name).where(Employee.id.in_(ids))
    name_map = {eid: n for eid, n in (await session.execute(names_stmt)).all()}
    submitter_name = name_map.get(ticket.submitter_id, "")
    if ticket.handler_id:
        handler_name = name_map.get(ticket.handler_id)

    return ITTicketResponse(
        ticket_id=ticket.id,
        ticket_no=ticket.ticket_no,
        type=ticket.type,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        submitter_id=ticket.submitter_id,
        submitter_name=submitter_name,
        handler_id=ticket.handler_id,
        handler_name=handler_name,
        resolution=ticket.resolution,
        resolved_at=ticket.resolved_at,
        created_at=ticket.created_at,
    )


# ── 员工设备查询 ─────────────────────────────────────────────


async def get_my_assets(session: AsyncSession, employee_id: int) -> list[ITAssetResponse]:
    """查询员工名下设备。"""
    logger.info("查询我的设备 | employee_id={eid}", eid=employee_id)
    stmt = select(ITAsset).where(
        ITAsset.employee_id == employee_id,
        ITAsset.status == "in_use",
    )
    assets = (await session.execute(stmt)).scalars().all()
    # 查员工姓名
    emp = (await session.execute(select(Employee.name).where(Employee.id == employee_id))).scalar_one_or_none()
    return [
        ITAssetResponse(
            asset_id=a.id,
            asset_no=a.asset_no,
            type=a.type,
            brand=a.brand,
            model_name=a.model_name,
            status=a.status,
            employee_id=a.employee_id,
            employee_name=emp,
            purchase_date=a.purchase_date,
            warranty_expire=a.warranty_expire,
        )
        for a in assets
    ]


# ── 工单创建 ─────────────────────────────────────────────────


async def create_ticket(
    session: AsyncSession,
    submitter_id: int,
    type: str,
    title: str,
    description: str = "",
    priority: str = "medium",
) -> ITTicketResponse:
    """创建 IT 工单。

    Args:
        submitter_id: 提交人 ID
        type: 工单类型
        title: 标题
        description: 描述
        priority: 优先级
    """
    logger.info("创建工单 | submitter_id={sid} type={t} priority={p}", sid=submitter_id, t=type, p=priority)
    # 生成工单编号
    max_id_stmt = select(func.max(ITTicket.id))
    max_id = (await session.execute(max_id_stmt)).scalar() or 0
    ticket_no = f"IT-T-{max_id + 1:04d}"

    ticket = ITTicket(
        ticket_no=ticket_no,
        type=type,
        title=title,
        description=description,
        status="open",
        priority=priority,
        submitter_id=submitter_id,
    )
    session.add(ticket)
    await session.flush()

    return ITTicketResponse(
        ticket_id=ticket.id,
        ticket_no=ticket.ticket_no,
        type=ticket.type,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        submitter_id=ticket.submitter_id,
        submitter_name="",
        created_at=ticket.created_at,
    )


# ── IT 管理员工单查询 ────────────────────────────────────────


async def get_all_tickets(
    session: AsyncSession,
    status: str | None = None,
    type: str | None = None,
    priority: str | None = None,
) -> list[ITTicketResponse]:
    """IT 管理员查询全部工单，支持多条件筛选。"""
    logger.info("管理员查询工单 | status={s} type={t} priority={p}", s=status or "全部", t=type or "全部", p=priority or "全部")
    stmt = (
        select(ITTicket, Employee.name.label("submitter_name"))
        .outerjoin(Employee, ITTicket.submitter_id == Employee.id)
        .order_by(ITTicket.created_at.desc())
    )
    if status:
        stmt = stmt.where(ITTicket.status == status)
    if type:
        stmt = stmt.where(ITTicket.type == type)
    if priority:
        stmt = stmt.where(ITTicket.priority == priority)
    rows = (await session.execute(stmt)).all()
    return [
        ITTicketResponse(
            ticket_id=t.id,
            ticket_no=t.ticket_no,
            type=t.type,
            title=t.title,
            status=t.status,
            priority=t.priority,
            submitter_id=t.submitter_id,
            submitter_name=name or "",
            handler_id=t.handler_id,
            created_at=t.created_at,
        )
        for t, name in rows
    ]


# ── IT 管理员工单处理 ────────────────────────────────────────


async def handle_ticket(
    session: AsyncSession,
    ticket_id: int,
    handler_id: int,
    action: str,
    resolution: str = "",
) -> ITTicketResponse:
    """IT 管理员处理工单（accept/resolve/close）。

    Args:
        ticket_id: 工单 ID
        handler_id: 处理人 ID
        action: 操作（accept/resolve/close）
        resolution: 处理结果说明（resolve 时填写）
    """
    logger.info("处理工单 | ticket_id={tid} action={act}", tid=ticket_id, act=action)
    ticket = (await session.execute(select(ITTicket).where(ITTicket.id == ticket_id))).scalar_one_or_none()
    if not ticket:
        raise NotFoundException(message="工单不存在")

    if action == "accept":
        if ticket.status != "open":
            raise BusinessException(message="仅待处理工单可受理")
        ticket.status = "in_progress"
        ticket.handler_id = handler_id
    elif action == "resolve":
        if ticket.status not in ("open", "in_progress"):
            raise BusinessException(message="仅待处理或处理中的工单可解决")
        ticket.status = "resolved"
        ticket.handler_id = handler_id
        ticket.resolution = resolution
        ticket.resolved_at = datetime.now(timezone.utc)
    elif action == "close":
        ticket.status = "closed"
    else:
        raise BusinessException(message=f"不支持的操作: {action}")

    await session.flush()
    return ITTicketResponse(
        ticket_id=ticket.id,
        ticket_no=ticket.ticket_no,
        type=ticket.type,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        submitter_id=ticket.submitter_id,
        submitter_name="",
        handler_id=ticket.handler_id,
        resolution=ticket.resolution,
        resolved_at=ticket.resolved_at,
        created_at=ticket.created_at,
    )


# ── IT 管理员设备查询 ────────────────────────────────────────


async def get_all_assets(
    session: AsyncSession,
    status: str | None = None,
    type: str | None = None,
) -> list[ITAssetResponse]:
    """IT 管理员查询全部设备。"""
    logger.info("管理员查询设备 | status={s} type={t}", s=status or "全部", t=type or "全部")
    stmt = (
        select(ITAsset, Employee.name.label("emp_name"))
        .outerjoin(Employee, ITAsset.employee_id == Employee.id)
        .order_by(ITAsset.id)
    )
    if status:
        stmt = stmt.where(ITAsset.status == status)
    if type:
        stmt = stmt.where(ITAsset.type == type)
    rows = (await session.execute(stmt)).all()
    return [
        ITAssetResponse(
            asset_id=a.id,
            asset_no=a.asset_no,
            type=a.type,
            brand=a.brand,
            model_name=a.model_name,
            status=a.status,
            employee_id=a.employee_id,
            employee_name=name,
            purchase_date=a.purchase_date,
            warranty_expire=a.warranty_expire,
        )
        for a, name in rows
    ]


# ── 设备分配与回收 ───────────────────────────────────────────


async def assign_asset(
    session: AsyncSession, asset_id: int, employee_id: int, operated_by: int,
) -> ITAssetResponse:
    """分配设备给员工。"""
    logger.info("分配设备 | asset_id={aid} → employee_id={eid}", aid=asset_id, eid=employee_id)
    asset = (await session.execute(select(ITAsset).where(ITAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise NotFoundException(message="设备不存在")
    if asset.status != "idle":
        raise BusinessException(message="设备当前不可分配（状态非空闲）")

    asset.status = "in_use"
    asset.employee_id = employee_id

    history = ITAssetHistory(
        asset_id=asset_id,
        action="assign",
        from_employee_id=None,
        to_employee_id=employee_id,
        operated_by=operated_by,
        remark="设备分配",
    )
    session.add(history)
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == employee_id))).scalar_one_or_none()
    return ITAssetResponse(
        asset_id=asset.id,
        asset_no=asset.asset_no,
        type=asset.type,
        brand=asset.brand,
        model_name=asset.model_name,
        status=asset.status,
        employee_id=asset.employee_id,
        employee_name=emp_name,
        purchase_date=asset.purchase_date,
        warranty_expire=asset.warranty_expire,
    )


async def reclaim_asset(
    session: AsyncSession, asset_id: int, operated_by: int,
) -> ITAssetResponse:
    """回收设备。"""
    logger.info("回收设备 | asset_id={aid}", aid=asset_id)
    asset = (await session.execute(select(ITAsset).where(ITAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise NotFoundException(message="设备不存在")
    if asset.status != "in_use":
        raise BusinessException(message="设备当前未被使用，无需回收")

    old_employee_id = asset.employee_id
    asset.status = "idle"
    asset.employee_id = None

    history = ITAssetHistory(
        asset_id=asset_id,
        action="reclaim",
        from_employee_id=old_employee_id,
        to_employee_id=None,
        operated_by=operated_by,
        remark="设备回收",
    )
    session.add(history)
    await session.flush()

    return ITAssetResponse(
        asset_id=asset.id,
        asset_no=asset.asset_no,
        type=asset.type,
        brand=asset.brand,
        model_name=asset.model_name,
        status=asset.status,
        employee_id=None,
        employee_name=None,
        purchase_date=asset.purchase_date,
        warranty_expire=asset.warranty_expire,
    )


# ── 统计报表 ─────────────────────────────────────────────────


async def ticket_stats(session: AsyncSession) -> ITTicketStatsResponse:
    """工单统计。"""
    logger.info("工单统计")
    # 按状态
    status_stmt = select(ITTicket.status, func.count()).group_by(ITTicket.status)
    by_status = dict((await session.execute(status_stmt)).all())
    # 按类型
    type_stmt = select(ITTicket.type, func.count()).group_by(ITTicket.type)
    by_type = dict((await session.execute(type_stmt)).all())
    # 按优先级
    prio_stmt = select(ITTicket.priority, func.count()).group_by(ITTicket.priority)
    by_priority = dict((await session.execute(prio_stmt)).all())
    # 平均处理时长
    avg_stmt = select(func.avg(
        func.julianday(ITTicket.resolved_at) - func.julianday(ITTicket.created_at),
    )).where(ITTicket.resolved_at.isnot(None))
    avg_days = (await session.execute(avg_stmt)).scalar()
    avg_hours = round(avg_days * 24, 1) if avg_days else None

    total = sum(by_status.values())
    return ITTicketStatsResponse(
        total=total, by_status=by_status, by_type=by_type, by_priority=by_priority, avg_resolve_hours=avg_hours,
    )


async def asset_stats(session: AsyncSession) -> ITAssetStatsResponse:
    """设备统计。"""
    logger.info("设备统计")
    # 按状态
    status_stmt = select(ITAsset.status, func.count()).group_by(ITAsset.status)
    by_status = dict((await session.execute(status_stmt)).all())
    # 按类型
    type_stmt = select(ITAsset.type, func.count()).group_by(ITAsset.type)
    by_type = dict((await session.execute(type_stmt)).all())
    # 按部门
    dept_stmt = (
        select(Department.name, func.count())
        .select_from(ITAsset)
        .join(Employee, ITAsset.employee_id == Employee.id)
        .join(Department, Employee.department_id == Department.id)
        .where(ITAsset.status == "in_use")
        .group_by(Department.name)
    )
    dept_rows = (await session.execute(dept_stmt)).all()
    by_department = [{"department": name, "count": cnt} for name, cnt in dept_rows]

    total = sum(by_status.values())
    return ITAssetStatsResponse(
        total=total, by_status=by_status, by_type=by_type, by_department=by_department,
    )


async def fault_trend(session: AsyncSession, months: int = 3) -> ITFaultTrendResponse:
    """故障趋势分析（近 N 个月）。"""
    logger.info("故障趋势分析 | months={m}", m=months)
    # 近 N 个月每月各类型工单数
    trend_stmt = (
        select(
            func.strftime("%Y-%m", ITTicket.created_at).label("month"),
            ITTicket.type,
            func.count().label("cnt"),
        )
        .where(ITTicket.created_at >= func.date("now", f"-{months} months"))
        .group_by("month", ITTicket.type)
        .order_by("month")
    )
    rows = (await session.execute(trend_stmt)).all()
    # 聚合成按月分组
    month_data: dict[str, dict[str, int]] = {}
    for month, ttype, cnt in rows:
        if month not in month_data:
            month_data[month] = {}
        month_data[month][ttype] = cnt
    trends = [
        FaultTrendItem(month=m, by_type=types, total=sum(types.values()))
        for m, types in month_data.items()
    ]

    # 高频故障部门 TOP5
    dept_stmt = (
        select(Department.name, func.count().label("cnt"))
        .select_from(ITTicket)
        .join(Employee, ITTicket.submitter_id == Employee.id)
        .join(Department, Employee.department_id == Department.id)
        .where(ITTicket.created_at >= func.date("now", f"-{months} months"))
        .group_by(Department.name)
        .order_by(func.count().desc())
        .limit(5)
    )
    dept_rows = (await session.execute(dept_stmt)).all()
    top_departments = [{"department": name, "ticket_count": cnt} for name, cnt in dept_rows]

    return ITFaultTrendResponse(trends=trends, top_departments=top_departments)
