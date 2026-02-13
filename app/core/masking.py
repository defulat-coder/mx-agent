"""敏感数据脱敏 — 手机号、邮箱、金额等字段自动打码"""

from collections.abc import Callable
from decimal import Decimal
from typing import Any


def mask_phone(val: Any) -> str:
    """手机号脱敏：138****0001"""
    s = str(val)
    if len(s) >= 7:
        return s[:3] + "****" + s[-4:]
    return "****"


def mask_email(val: Any) -> str:
    """邮箱脱敏：zha***@maxi.com"""
    s = str(val)
    if "@" in s:
        local, domain = s.split("@", 1)
        visible = min(3, len(local))
        return local[:visible] + "***@" + domain
    return "***"


def mask_amount(val: Any) -> str:
    """金额脱敏：完全遮蔽"""
    return "***"


def mask_id_card(val: Any) -> str:
    """身份证脱敏：110***********1234"""
    s = str(val)
    if len(s) >= 8:
        return s[:3] + "*" * (len(s) - 7) + s[-4:]
    return "****"


# 敏感字段 → 脱敏函数映射
SENSITIVE_FIELDS: dict[str, Callable[[Any], str]] = {
    # 个人信息
    "phone": mask_phone,
    "email": mask_email,
    # 薪资
    "base_salary": mask_amount,
    "bonus": mask_amount,
    "allowance": mask_amount,
    "deduction": mask_amount,
    "social_insurance": mask_amount,
    "housing_fund": mask_amount,
    "tax": mask_amount,
    "net_salary": mask_amount,
    # 社保公积金
    "pension": mask_amount,
    "medical": mask_amount,
    "unemployment": mask_amount,
    "pension_company": mask_amount,
    "medical_company": mask_amount,
    "unemployment_company": mask_amount,
    "injury_company": mask_amount,
    "maternity_company": mask_amount,
    "housing_fund_company": mask_amount,
}


def mask_dict(data: dict[str, Any], rules: dict[str, Callable[[Any], str]] | None = None) -> dict[str, Any]:
    """对 dict 中的敏感字段自动脱敏，返回脱敏后的副本。

    Args:
        data: 原始数据字典
        rules: 字段→脱敏函数映射，默认使用 SENSITIVE_FIELDS

    Returns:
        脱敏后的字典副本
    """
    if rules is None:
        rules = SENSITIVE_FIELDS
    result = dict(data)
    for key, mask_fn in rules.items():
        if key in result and result[key] is not None:
            result[key] = mask_fn(result[key])
    return result
