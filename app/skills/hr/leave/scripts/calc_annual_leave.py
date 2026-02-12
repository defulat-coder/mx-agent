"""
年假天数计算

根据社会工龄和司龄计算员工可享受的年假总天数
"""

from datetime import date
import math


def calc_legal_annual_leave(total_working_years: int) -> int:
    """计算法定年假天数"""
    if total_working_years < 1:
        return 0
    if total_working_years < 10:
        return 5
    if total_working_years < 20:
        return 10
    return 15


def calc_company_extra_leave(company_years: int) -> int:
    """计算公司额外福利年假"""
    if company_years >= 10:
        return 5
    if company_years >= 5:
        return 3
    if company_years >= 3:
        return 2
    if company_years >= 1:
        return 1
    return 0


def calc_prorated_leave(total_days: int, hire_date: date, year: int) -> int:
    """入职当年按剩余日历天数折算"""
    if hire_date.year < year:
        return total_days

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    remaining_days = (year_end - hire_date).days + 1
    total_year_days = (year_end - year_start).days + 1

    prorated = total_days * remaining_days / total_year_days
    return math.floor(prorated)  # 不足1天不计


def calc_annual_leave(
    hire_date: date,
    total_working_years: int,
    year: int | None = None,
) -> dict:
    """
    计算年假总天数

    Args:
        hire_date: 入职日期
        total_working_years: 累计社会工龄（年）
        year: 计算年份，默认当年
    """
    if year is None:
        year = date.today().year

    company_years = year - hire_date.year
    if date(year, hire_date.month, hire_date.day) > date(year, 12, 31):
        company_years -= 1

    legal_days = calc_legal_annual_leave(total_working_years)
    extra_days = calc_company_extra_leave(company_years)
    total_days = legal_days + extra_days

    # 入职当年折算
    final_days = calc_prorated_leave(total_days, hire_date, year)

    return {
        "year": year,
        "total_working_years": total_working_years,
        "company_years": company_years,
        "legal_annual_leave": legal_days,
        "company_extra_leave": extra_days,
        "total_before_prorate": total_days,
        "final_days": final_days,
        "note": "入职当年按剩余日历天数折算" if hire_date.year == year else None,
    }
