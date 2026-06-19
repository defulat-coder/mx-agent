"""行政员工操作 Tools — 预订会议室、申领用品、预约访客、差旅申请"""

import json
from datetime import datetime

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import admin as admin_service
from app.tools.hr.utils import get_employee_id


async def adm_book_room(
    run_context: RunContext,
    room_id: int,
    title: str,
    start_time: str,
    end_time: str,
) -> str:
    """预订会议室。时间必须为 30 分钟整点（:00 或 :30），最多提前 7 天。

    Args:
        room_id: 会议室 ID
        title: 会议主题
        start_time: 开始时间（ISO 格式，如 2026-02-14T09:00:00）
        end_time: 结束时间（ISO 格式，如 2026-02-14T10:00:00）
    """
    logger.info("tool=adm_book_room | room_id={r} title={t}", r=room_id, t=title)
    employee_id = get_employee_id(run_context)
    st = datetime.fromisoformat(start_time)
    et = datetime.fromisoformat(end_time)
    async with async_session_factory() as session:
        try:
            record = await admin_service.book_room(session, employee_id, room_id, title, st, et)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def adm_cancel_booking(run_context: RunContext, booking_id: int) -> str:
    """取消会议室预订。仅限自己的预订，且需在开始前 30 分钟之前。

    Args:
        booking_id: 预订 ID
    """
    logger.info("tool=adm_cancel_booking | booking_id={bid}", bid=booking_id)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        try:
            record = await admin_service.cancel_booking(session, booking_id, employee_id)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def adm_request_supply(run_context: RunContext, items: str) -> str:
    """申领办公用品。提交申领单，等待行政人员审批。

    Args:
        items: 申领物品列表，JSON 格式，如 [{"name":"A4纸","quantity":2},{"name":"签字笔","quantity":5}]
    """
    logger.info("tool=adm_request_supply")
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        record = await admin_service.request_supply(session, employee_id, items)
        await session.commit()
        return record.model_dump_json()


async def adm_book_visitor(
    run_context: RunContext,
    visitor_name: str,
    visit_date: str,
    company: str = "",
    phone: str = "",
    visit_time: str = "",
    purpose: str = "",
) -> str:
    """预约访客来访登记。

    Args:
        visitor_name: 访客姓名
        visit_date: 来访日期（YYYY-MM-DD）
        company: 来访单位
        phone: 联系电话
        visit_time: 来访时间段（如 09:00-10:00）
        purpose: 来访目的
    """
    logger.info("tool=adm_book_visitor | visitor={vn}", vn=visitor_name)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        record = await admin_service.book_visitor(
            session, employee_id, visitor_name, company, phone, visit_date, visit_time, purpose,
        )
        await session.commit()
        return record.model_dump_json()


async def adm_apply_travel(
    run_context: RunContext,
    destination: str,
    start_date: str,
    end_date: str,
    reason: str = "",
) -> str:
    """申请差旅。不创建数据库记录，返回 OA 审批链接。

    Args:
        destination: 目的地
        start_date: 出发日期（YYYY-MM-DD）
        end_date: 返回日期（YYYY-MM-DD）
        reason: 出差事由
    """
    logger.info("tool=adm_apply_travel | dest={d}", d=destination)
    employee_id = get_employee_id(run_context)
    result = {
        "approval_url": f"https://oa.maxi.com/travel/apply?employee_id={employee_id}&dest={destination}&start={start_date}&end={end_date}",
        "message": "差旅申请已提交，请前往 OA 系统完成审批流程",
    }
    return json.dumps(result, ensure_ascii=False)
