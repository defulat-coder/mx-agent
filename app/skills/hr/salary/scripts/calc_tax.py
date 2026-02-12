"""
个人所得税估算（累计预扣法）

按照中国现行个税政策计算月度应预扣预缴税额
"""

# 综合所得税率表
TAX_BRACKETS = [
    (36_000, 0.03, 0),
    (144_000, 0.10, 2_520),
    (300_000, 0.20, 16_920),
    (420_000, 0.25, 31_920),
    (660_000, 0.30, 52_920),
    (960_000, 0.35, 85_920),
    (float("inf"), 0.45, 181_920),
]


def calc_cumulative_tax(cumulative_taxable_income: float) -> float:
    """根据累计应纳税所得额计算累计应纳税额"""
    for threshold, rate, deduction in TAX_BRACKETS:
        if cumulative_taxable_income <= threshold:
            return cumulative_taxable_income * rate - deduction
    return 0.0


def calc_monthly_tax(
    monthly_salary: float,
    social_insurance: float,
    housing_fund: float,
    special_deduction: float = 0.0,
    month: int = 1,
    cumulative_income_prev: float = 0.0,
    cumulative_tax_prev: float = 0.0,
) -> dict:
    """
    计算当月应预扣预缴个税

    Args:
        monthly_salary: 当月应发工资（税前）
        social_insurance: 社保个人部分
        housing_fund: 公积金个人部分
        special_deduction: 专项附加扣除合计（子女教育、房贷等）
        month: 当前月份（1-12）
        cumulative_income_prev: 截至上月的累计应纳税所得额
        cumulative_tax_prev: 截至上月的累计已预扣税额
    """
    # 起征点
    threshold = 5_000

    # 当月应纳税所得额
    taxable_income = monthly_salary - social_insurance - housing_fund - threshold - special_deduction
    taxable_income = max(0, taxable_income)

    # 累计应纳税所得额
    cumulative_taxable = cumulative_income_prev + taxable_income

    # 累计应纳税额
    cumulative_tax = calc_cumulative_tax(cumulative_taxable)

    # 当月应预扣税额
    current_tax = max(0, cumulative_tax - cumulative_tax_prev)

    # 实发工资
    net_salary = monthly_salary - social_insurance - housing_fund - current_tax

    return {
        "month": month,
        "gross_salary": monthly_salary,
        "social_insurance": social_insurance,
        "housing_fund": housing_fund,
        "special_deduction": special_deduction,
        "taxable_income": round(taxable_income, 2),
        "cumulative_taxable_income": round(cumulative_taxable, 2),
        "tax": round(current_tax, 2),
        "net_salary": round(net_salary, 2),
    }
