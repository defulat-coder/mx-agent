"""财务相关响应 Schema"""

import datetime as dt

from pydantic import BaseModel, Field


class ReimbursementItemResponse(BaseModel):
    """报销明细行"""

    item_id: int = Field(description="明细 ID")
    description: str = Field(description="费用说明")
    amount: float = Field(description="金额")
    expense_date: dt.date = Field(description="费用日期")
    category: str = Field(description="费用科目")


class ReimbursementResponse(BaseModel):
    """报销单"""

    reimbursement_id: int = Field(description="报销单 ID")
    reimbursement_no: str = Field(description="报销单号")
    employee_id: int = Field(description="申请人 ID")
    employee_name: str = Field(default="", description="申请人姓名")
    type: str = Field(description="报销类型")
    amount: float = Field(description="报销金额")
    status: str = Field(description="状态")
    department_name: str = Field(default="", description="部门名称")
    reviewer_id: int | None = Field(default=None, description="审核人 ID")
    review_remark: str = Field(default="", description="审核备注")
    reviewed_at: dt.datetime | None = Field(default=None, description="审核时间")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")
    items: list[ReimbursementItemResponse] = Field(default_factory=list, description="明细行")


class BudgetResponse(BaseModel):
    """部门预算"""

    budget_id: int = Field(description="预算 ID")
    department_id: int = Field(description="部门 ID")
    department_name: str = Field(default="", description="部门名称")
    year: int = Field(description="年度")
    total_amount: float = Field(description="预算总额")
    used_amount: float = Field(description="已使用金额")
    remaining: float = Field(description="剩余金额")
    usage_rate: float = Field(description="执行率（%）")
    status: str = Field(description="状态")


class BudgetUsageResponse(BaseModel):
    """预算使用记录"""

    usage_id: int = Field(description="使用记录 ID")
    budget_id: int = Field(description="预算 ID")
    amount: float = Field(description="使用金额")
    category: str = Field(description="费用科目")
    description: str = Field(default="", description="说明")
    used_date: dt.date = Field(description="使用日期")


class PayableResponse(BaseModel):
    """应付款"""

    payable_id: int = Field(description="应付款 ID")
    payable_no: str = Field(description="应付单号")
    vendor: str = Field(description="供应商")
    amount: float = Field(description="金额")
    due_date: dt.date = Field(description="到期日")
    status: str = Field(description="状态")
    description: str = Field(default="", description="说明")


class ReceivableResponse(BaseModel):
    """应收款"""

    receivable_id: int = Field(description="应收款 ID")
    receivable_no: str = Field(description="应收单号")
    customer: str = Field(description="客户")
    amount: float = Field(description="金额")
    due_date: dt.date = Field(description="到期日")
    status: str = Field(description="状态")
    description: str = Field(default="", description="说明")


class TaxRecord(BaseModel):
    """个税记录"""

    year_month: str = Field(description="月份")
    gross_salary: float = Field(description="税前工资")
    tax: float = Field(description="个人所得税")
    net_salary: float = Field(description="税后工资")


class ExpenseSummaryItem(BaseModel):
    """费用汇总项"""

    key: str = Field(description="分组键")
    total_amount: float = Field(description="合计金额")
    count: int = Field(description="笔数")


class BudgetAlertItem(BaseModel):
    """预算预警项"""

    department_name: str = Field(description="部门名称")
    year: int = Field(description="年度")
    total_amount: float = Field(description="预算总额")
    used_amount: float = Field(description="已使用金额")
    usage_rate: float = Field(description="执行率（%）")
