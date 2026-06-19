"""财务管理 Service — 报销、预算、应收应付、个税"""

from datetime import date, datetime, timezone

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, NotFoundException
from app.models.finance import Budget, BudgetUsage, Payable, Receivable, Reimbursement, ReimbursementItem
from app.models.hr import Department, Employee
from app.models.hr.salary import SalaryRecord
from app.schemas.finance import (
    BudgetAlertItem,
    BudgetResponse,
    BudgetUsageResponse,
    ExpenseSummaryItem,
    PayableResponse,
    ReceivableResponse,
    ReimbursementItemResponse,
    ReimbursementResponse,
    TaxRecord,
)


# ── 辅助 ─────────────────────────────────────────────────


def _budget_to_response(b: Budget, dept_name: str = "") -> BudgetResponse:
    remaining = b.total_amount - b.used_amount
    rate = round(b.used_amount / b.total_amount * 100, 1) if b.total_amount > 0 else 0
    return BudgetResponse(
        budget_id=b.id, department_id=b.department_id, department_name=dept_name,
        year=b.year, total_amount=b.total_amount, used_amount=b.used_amount,
        remaining=remaining, usage_rate=rate, status=b.status,
    )


# ── 员工报销查询 ──────────────────────────────────────────


async def get_my_reimbursements(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[ReimbursementResponse]:
    """查询员工本人报销单列表。"""
    logger.info("查询我的报销单 | employee_id={eid} status={s}", eid=employee_id, s=status or "全部")
    stmt = (
        select(Reimbursement, Department.name.label("dept_name"))
        .outerjoin(Department, Reimbursement.department_id == Department.id)
        .where(Reimbursement.employee_id == employee_id)
        .order_by(Reimbursement.created_at.desc())
    )
    if status:
        stmt = stmt.where(Reimbursement.status == status)
    rows = (await session.execute(stmt)).all()
    return [
        ReimbursementResponse(
            reimbursement_id=r.id, reimbursement_no=r.reimbursement_no,
            employee_id=r.employee_id, type=r.type, amount=r.amount,
            status=r.status, department_name=dn or "",
            reviewer_id=r.reviewer_id, review_remark=r.review_remark,
            reviewed_at=r.reviewed_at, created_at=r.created_at,
        )
        for r, dn in rows
    ]


async def get_reimbursement_detail(
    session: AsyncSession, reimbursement_id: int, employee_id: int | None = None,
) -> ReimbursementResponse:
    """查询报销单详情（含明细行）。"""
    logger.info("查询报销单详情 | reimbursement_id={rid}", rid=reimbursement_id)
    r = (await session.execute(select(Reimbursement).where(Reimbursement.id == reimbursement_id))).scalar_one_or_none()
    if not r:
        raise NotFoundException(message="报销单不存在")
    if employee_id is not None and r.employee_id != employee_id:
        raise BusinessException(message="无权查看此报销单")

    # 查明细
    items_stmt = select(ReimbursementItem).where(ReimbursementItem.reimbursement_id == reimbursement_id)
    items = (await session.execute(items_stmt)).scalars().all()

    # 查姓名和部门
    emp_name = (await session.execute(select(Employee.name).where(Employee.id == r.employee_id))).scalar_one_or_none() or ""
    dept_name = (await session.execute(select(Department.name).where(Department.id == r.department_id))).scalar_one_or_none() or ""

    return ReimbursementResponse(
        reimbursement_id=r.id, reimbursement_no=r.reimbursement_no,
        employee_id=r.employee_id, employee_name=emp_name,
        type=r.type, amount=r.amount, status=r.status,
        department_name=dept_name, reviewer_id=r.reviewer_id,
        review_remark=r.review_remark, reviewed_at=r.reviewed_at,
        created_at=r.created_at,
        items=[
            ReimbursementItemResponse(
                item_id=it.id, description=it.description, amount=it.amount,
                expense_date=it.expense_date, category=it.category,
            )
            for it in items
        ],
    )


# ── 员工预算查询 ──────────────────────────────────────────


async def get_department_budget(
    session: AsyncSession, department_id: int, year: int | None = None,
) -> BudgetResponse | None:
    """查询部门当年预算。"""
    logger.info("查询部门预算 | department_id={did} year={y}", did=department_id, y=year)
    y = year or date.today().year
    stmt = (
        select(Budget, Department.name.label("dept_name"))
        .outerjoin(Department, Budget.department_id == Department.id)
        .where(Budget.department_id == department_id, Budget.year == y)
    )
    row = (await session.execute(stmt)).first()
    if not row:
        return None
    b, dn = row
    return _budget_to_response(b, dn or "")


# ── 员工个税查询（跨域读 HR） ────────────────────────────


async def get_my_tax(
    session: AsyncSession, employee_id: int, year_month: str | None = None,
) -> list[TaxRecord]:
    """查询个税明细，跨域读 HR SalaryRecord。"""
    logger.info("查询个税 | employee_id={eid} year_month={ym}", eid=employee_id, ym=year_month or "近3月")
    stmt = (
        select(SalaryRecord)
        .where(SalaryRecord.employee_id == employee_id)
        .order_by(SalaryRecord.year_month.desc())
    )
    if year_month:
        stmt = stmt.where(SalaryRecord.year_month == year_month)
    else:
        stmt = stmt.limit(3)
    records = (await session.execute(stmt)).scalars().all()
    return [
        TaxRecord(
            year_month=r.year_month,
            gross_salary=float(r.base_salary + r.bonus + r.allowance),
            tax=float(r.tax),
            net_salary=float(r.net_salary),
        )
        for r in records
    ]


# ── 主管：预算总览 ───────────────────────────────────────


async def get_budget_overview(
    session: AsyncSession, department_id: int,
) -> list[BudgetResponse]:
    """主管查看部门预算总览。"""
    logger.info("主管查看预算总览 | department_id={did}", did=department_id)
    stmt = (
        select(Budget, Department.name.label("dept_name"))
        .outerjoin(Department, Budget.department_id == Department.id)
        .where(Budget.department_id == department_id)
        .order_by(Budget.year.desc())
    )
    rows = (await session.execute(stmt)).all()
    return [_budget_to_response(b, dn or "") for b, dn in rows]


async def get_expense_detail(
    session: AsyncSession, department_id: int,
    category: str | None = None, year_month: str | None = None,
) -> list[BudgetUsageResponse]:
    """主管查看部门费用明细。"""
    logger.info("主管查看费用明细 | department_id={did}", did=department_id)
    stmt = (
        select(BudgetUsage)
        .join(Budget, BudgetUsage.budget_id == Budget.id)
        .where(Budget.department_id == department_id)
        .order_by(BudgetUsage.used_date.desc())
    )
    if category:
        stmt = stmt.where(BudgetUsage.category == category)
    if year_month:
        stmt = stmt.where(func.strftime("%Y-%m", BudgetUsage.used_date) == year_month)
    records = (await session.execute(stmt)).scalars().all()
    return [
        BudgetUsageResponse(
            usage_id=u.id, budget_id=u.budget_id, amount=u.amount,
            category=u.category, description=u.description, used_date=u.used_date,
        )
        for u in records
    ]


async def get_budget_alert(
    session: AsyncSession, department_id: int,
) -> list[BudgetAlertItem]:
    """主管查看预算预警（执行率超 80%）。"""
    logger.info("主管查看预算预警 | department_id={did}", did=department_id)
    stmt = (
        select(Budget, Department.name.label("dept_name"))
        .outerjoin(Department, Budget.department_id == Department.id)
        .where(Budget.department_id == department_id, Budget.status == "active")
    )
    rows = (await session.execute(stmt)).all()
    alerts = []
    for b, dn in rows:
        rate = round(b.used_amount / b.total_amount * 100, 1) if b.total_amount > 0 else 0
        if rate >= 80:
            alerts.append(BudgetAlertItem(
                department_name=dn or "", year=b.year,
                total_amount=b.total_amount, used_amount=b.used_amount, usage_rate=rate,
            ))
    return alerts


# ── 财务人员：报销查询 ───────────────────────────────────


async def get_all_reimbursements(
    session: AsyncSession,
    status: str | None = None,
    type: str | None = None,
    department_id: int | None = None,
) -> list[ReimbursementResponse]:
    """财务人员查询全部报销单。"""
    logger.info("财务查询全部报销单 | status={s} type={t} dept={d}", s=status, t=type, d=department_id)
    stmt = (
        select(Reimbursement, Employee.name.label("emp_name"), Department.name.label("dept_name"))
        .outerjoin(Employee, Reimbursement.employee_id == Employee.id)
        .outerjoin(Department, Reimbursement.department_id == Department.id)
        .order_by(Reimbursement.created_at.desc())
    )
    if status:
        stmt = stmt.where(Reimbursement.status == status)
    if type:
        stmt = stmt.where(Reimbursement.type == type)
    if department_id:
        stmt = stmt.where(Reimbursement.department_id == department_id)
    rows = (await session.execute(stmt)).all()
    return [
        ReimbursementResponse(
            reimbursement_id=r.id, reimbursement_no=r.reimbursement_no,
            employee_id=r.employee_id, employee_name=en or "",
            type=r.type, amount=r.amount, status=r.status,
            department_name=dn or "", reviewer_id=r.reviewer_id,
            review_remark=r.review_remark, reviewed_at=r.reviewed_at,
            created_at=r.created_at,
        )
        for r, en, dn in rows
    ]


# ── 财务人员：费用汇总 ──────────────────────────────────


async def get_expense_summary(
    session: AsyncSession, group_by: str = "department",
) -> list[ExpenseSummaryItem]:
    """费用汇总（按部门/科目/月度）。"""
    logger.info("费用汇总 | group_by={g}", g=group_by)
    if group_by == "department":
        stmt = (
            select(Department.name, func.sum(Reimbursement.amount), func.count())
            .select_from(Reimbursement)
            .join(Department, Reimbursement.department_id == Department.id)
            .where(Reimbursement.status.in_(["approved", "paid"]))
            .group_by(Department.name)
            .order_by(func.sum(Reimbursement.amount).desc())
        )
    elif group_by == "type":
        stmt = (
            select(Reimbursement.type, func.sum(Reimbursement.amount), func.count())
            .where(Reimbursement.status.in_(["approved", "paid"]))
            .group_by(Reimbursement.type)
            .order_by(func.sum(Reimbursement.amount).desc())
        )
    else:
        stmt = (
            select(
                func.strftime("%Y-%m", Reimbursement.created_at).label("month"),
                func.sum(Reimbursement.amount),
                func.count(),
            )
            .where(Reimbursement.status.in_(["approved", "paid"]))
            .group_by("month")
            .order_by("month")
        )
    rows = (await session.execute(stmt)).all()
    return [ExpenseSummaryItem(key=k or "", total_amount=round(a, 2), count=c) for k, a, c in rows]


# ── 财务人员：预算执行分析 ───────────────────────────────


async def get_budget_analysis(session: AsyncSession) -> list[BudgetResponse]:
    """全公司预算执行分析。"""
    logger.info("全公司预算执行分析")
    current_year = date.today().year
    stmt = (
        select(Budget, Department.name.label("dept_name"))
        .outerjoin(Department, Budget.department_id == Department.id)
        .where(Budget.year == current_year)
        .order_by(Budget.department_id)
    )
    rows = (await session.execute(stmt)).all()
    return [_budget_to_response(b, dn or "") for b, dn in rows]


# ── 财务人员：应收应付 ──────────────────────────────────


async def get_payables(
    session: AsyncSession, status: str | None = None,
) -> list[PayableResponse]:
    """查询应付款。"""
    logger.info("查询应付款 | status={s}", s=status or "全部")
    stmt = select(Payable).order_by(Payable.due_date)
    if status:
        stmt = stmt.where(Payable.status == status)
    records = (await session.execute(stmt)).scalars().all()
    return [
        PayableResponse(
            payable_id=p.id, payable_no=p.payable_no, vendor=p.vendor,
            amount=p.amount, due_date=p.due_date, status=p.status,
            description=p.description,
        )
        for p in records
    ]


async def get_receivables(
    session: AsyncSession, status: str | None = None,
) -> list[ReceivableResponse]:
    """查询应收款。"""
    logger.info("查询应收款 | status={s}", s=status or "全部")
    stmt = select(Receivable).order_by(Receivable.due_date)
    if status:
        stmt = stmt.where(Receivable.status == status)
    records = (await session.execute(stmt)).scalars().all()
    return [
        ReceivableResponse(
            receivable_id=r.id, receivable_no=r.receivable_no, customer=r.customer,
            amount=r.amount, due_date=r.due_date, status=r.status,
            description=r.description,
        )
        for r in records
    ]


# ── 财务人员：报销审核 ──────────────────────────────────


async def review_reimbursement(
    session: AsyncSession, reimbursement_id: int, reviewer_id: int,
    action: str, remark: str = "",
) -> ReimbursementResponse:
    """审核报销单。

    Args:
        reimbursement_id: 报销单 ID
        reviewer_id: 审核人 ID
        action: approve/reject/return
        remark: 审核备注
    """
    logger.info("审核报销单 | id={rid} action={act}", rid=reimbursement_id, act=action)
    r = (await session.execute(select(Reimbursement).where(Reimbursement.id == reimbursement_id))).scalar_one_or_none()
    if not r:
        raise NotFoundException(message="报销单不存在")
    if r.status not in ("pending", "returned"):
        raise BusinessException(message=f"当前状态 [{r.status}] 不允许审核")

    if action == "approve":
        r.status = "approved"
        # 关联预算扣减
        current_year = date.today().year
        budget = (await session.execute(
            select(Budget).where(Budget.department_id == r.department_id, Budget.year == current_year),
        )).scalar_one_or_none()
        if budget:
            budget.used_amount += r.amount
            usage = BudgetUsage(
                budget_id=budget.id, reimbursement_id=r.id, amount=r.amount,
                category=r.type, description=f"报销单 {r.reimbursement_no}",
                used_date=date.today(),
            )
            session.add(usage)
    elif action == "reject":
        r.status = "rejected"
    elif action == "return":
        r.status = "returned"
    else:
        raise BusinessException(message=f"不支持的操作: {action}")

    r.reviewer_id = reviewer_id
    r.review_remark = remark
    r.reviewed_at = datetime.now(timezone.utc)
    await session.flush()

    emp_name = (await session.execute(select(Employee.name).where(Employee.id == r.employee_id))).scalar_one_or_none() or ""
    dept_name = (await session.execute(select(Department.name).where(Department.id == r.department_id))).scalar_one_or_none() or ""

    return ReimbursementResponse(
        reimbursement_id=r.id, reimbursement_no=r.reimbursement_no,
        employee_id=r.employee_id, employee_name=emp_name,
        type=r.type, amount=r.amount, status=r.status,
        department_name=dept_name, reviewer_id=r.reviewer_id,
        review_remark=r.review_remark, reviewed_at=r.reviewed_at,
        created_at=r.created_at,
    )
