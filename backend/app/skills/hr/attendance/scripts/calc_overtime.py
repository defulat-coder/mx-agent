"""
加班时长与补偿计算

输入：加班类型、开始时间、结束时间
输出：有效加班时长、补偿方式与金额
"""

from datetime import datetime
from enum import Enum


class OvertimeType(Enum):
    WORKDAY = "workday"        # 工作日
    WEEKEND = "weekend"        # 周末
    HOLIDAY = "holiday"        # 法定节假日


def calc_overtime_hours(start: datetime, end: datetime, overtime_type: OvertimeType) -> dict:
    """计算有效加班时长"""
    total_minutes = (end - start).total_seconds() / 60

    # 扣除用餐时间（如跨越 18:00-18:30）
    meal_start = start.replace(hour=18, minute=0, second=0)
    meal_end = start.replace(hour=18, minute=30, second=0)
    if start < meal_end and end > meal_start:
        overlap_start = max(start, meal_start)
        overlap_end = min(end, meal_end)
        total_minutes -= max(0, (overlap_end - overlap_start).total_seconds() / 60)

    hours = round(total_minutes / 60, 1)

    # 工作日加班不足1小时不计
    if overtime_type == OvertimeType.WORKDAY and hours < 1:
        return {"valid": False, "hours": 0, "reason": "工作日加班不足1小时，不计入加班"}

    return {"valid": True, "hours": hours}


def calc_overtime_compensation(
    hours: float,
    overtime_type: OvertimeType,
    monthly_salary: float,
    prefer_leave: bool = True,
) -> dict:
    """
    计算加班补偿

    Args:
        hours: 加班时长
        overtime_type: 加班类型
        monthly_salary: 月薪（用于计算加班费基数）
        prefer_leave: 是否优先选择调休（仅周末加班可选）
    """
    # 日薪 = 月薪 / 21.75
    daily_rate = monthly_salary / 21.75
    hourly_rate = daily_rate / 8

    if overtime_type == OvertimeType.WORKDAY:
        return {
            "type": "调休",
            "leave_hours": hours,
            "note": "工作日加班按 1:1 调休，调休有效期6个月",
        }

    if overtime_type == OvertimeType.WEEKEND:
        if prefer_leave:
            return {
                "type": "调休",
                "leave_hours": hours,
                "note": "周末加班按 1:1 调休，调休有效期6个月",
            }
        return {
            "type": "加班费",
            "rate": "200%",
            "amount": round(hourly_rate * 2 * hours, 2),
            "note": "周末加班费 = 小时工资 × 200% × 加班时长",
        }

    if overtime_type == OvertimeType.HOLIDAY:
        return {
            "type": "加班费",
            "rate": "300%",
            "amount": round(hourly_rate * 3 * hours, 2),
            "note": "法定节假日加班费 = 小时工资 × 300% × 加班时长",
        }
