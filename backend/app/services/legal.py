"""法务管理 Service — 合同模板、合同管理、审查、条款分析"""

import json
from datetime import date, timedelta

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, NotFoundException
from app.core.llm import get_model
from app.models.legal import Contract, ContractReview, ContractTemplate
from app.models.hr import Department, Employee
from app.schemas.legal import (
    ContractAnalysisResult,
    ContractResponse,
    ContractReviewResponse,
    ContractStatsResponse,
    ContractTemplateResponse,
)


# ── 辅助 ─────────────────────────────────────────────────


def _contract_to_response(c: Contract, emp_name: str = "", dept_name: str = "") -> ContractResponse:
    return ContractResponse(
        contract_id=c.id, contract_no=c.contract_no, title=c.title,
        type=c.type, party_a=c.party_a, party_b=c.party_b,
        amount=float(c.amount), start_date=c.start_date, end_date=c.end_date,
        status=c.status, submitted_by=c.submitted_by,
        submitted_name=emp_name, department_name=dept_name,
        created_at=c.created_at,
    )


# ── 合同模板查询 ─────────────────────────────────────────


async def get_templates(
    session: AsyncSession, type: str | None = None,
) -> list[ContractTemplateResponse]:
    """查询合同模板列表。"""
    logger.info("查询合同模板 | type={t}", t=type or "全部")
    stmt = select(ContractTemplate).order_by(ContractTemplate.type, ContractTemplate.name)
    if type:
        stmt = stmt.where(ContractTemplate.type == type)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        ContractTemplateResponse(
            template_id=t.id, name=t.name, type=t.type,
            description=t.description, file_url=t.file_url,
        )
        for t in rows
    ]


async def get_template_detail(
    session: AsyncSession, template_id: int,
) -> ContractTemplateResponse:
    """查询合同模板详情。"""
    logger.info("查询模板详情 | template_id={tid}", tid=template_id)
    t = (await session.execute(select(ContractTemplate).where(ContractTemplate.id == template_id))).scalar_one_or_none()
    if not t:
        raise NotFoundException(message="合同模板不存在")
    return ContractTemplateResponse(
        template_id=t.id, name=t.name, type=t.type,
        description=t.description, file_url=t.file_url,
    )


# ── 员工合同查询 ─────────────────────────────────────────


async def get_my_contracts(
    session: AsyncSession, employee_id: int, status: str | None = None,
) -> list[ContractResponse]:
    """查询员工提交的合同列表。"""
    logger.info("查询我的合同 | employee_id={eid} status={s}", eid=employee_id, s=status or "全部")
    stmt = (
        select(Contract, Department.name.label("dept_name"))
        .outerjoin(Department, Contract.department_id == Department.id)
        .where(Contract.submitted_by == employee_id)
        .order_by(Contract.created_at.desc())
    )
    if status:
        stmt = stmt.where(Contract.status == status)
    rows = (await session.execute(stmt)).all()
    return [_contract_to_response(c, dept_name=dn or "") for c, dn in rows]


# ── 法务人员：合同台账 ───────────────────────────────────


async def get_all_contracts(
    session: AsyncSession,
    type: str | None = None,
    status: str | None = None,
    department_id: int | None = None,
) -> list[ContractResponse]:
    """法务人员查询全部合同台账。"""
    logger.info("法务查询全部合同 | type={t} status={s} dept={d}", t=type, s=status, d=department_id)
    stmt = (
        select(Contract, Employee.name.label("emp_name"), Department.name.label("dept_name"))
        .outerjoin(Employee, Contract.submitted_by == Employee.id)
        .outerjoin(Department, Contract.department_id == Department.id)
        .order_by(Contract.created_at.desc())
    )
    if type:
        stmt = stmt.where(Contract.type == type)
    if status:
        stmt = stmt.where(Contract.status == status)
    if department_id:
        stmt = stmt.where(Contract.department_id == department_id)
    rows = (await session.execute(stmt)).all()
    return [_contract_to_response(c, en or "", dn or "") for c, en, dn in rows]


# ── 法务人员：合同审查 ───────────────────────────────────


async def review_contract(
    session: AsyncSession, contract_id: int, reviewer_id: int,
    action: str, opinion: str = "",
) -> ContractReviewResponse:
    """审查合同。

    Args:
        contract_id: 合同 ID
        reviewer_id: 审查人 ID
        action: approved/returned
        opinion: 审查意见
    """
    logger.info("审查合同 | id={cid} action={act}", cid=contract_id, act=action)
    c = (await session.execute(select(Contract).where(Contract.id == contract_id))).scalar_one_or_none()
    if not c:
        raise NotFoundException(message="合同不存在")
    if c.status != "pending":
        raise BusinessException(message=f"该合同当前状态 [{c.status}] 不可审查，仅 pending 状态可审查")

    if action == "approved":
        c.status = "approved"
    elif action == "returned":
        c.status = "returned"
    else:
        raise BusinessException(message=f"不支持的操作: {action}，仅支持 approved/returned")

    review = ContractReview(
        contract_id=contract_id,
        reviewer_id=reviewer_id,
        action=action,
        opinion=opinion,
    )
    session.add(review)
    await session.flush()

    reviewer_name = (await session.execute(select(Employee.name).where(Employee.id == reviewer_id))).scalar_one_or_none() or ""

    return ContractReviewResponse(
        review_id=review.id, contract_id=contract_id,
        reviewer_id=reviewer_id, reviewer_name=reviewer_name,
        action=action, opinion=opinion, created_at=review.created_at,
    )


# ── 法务人员：到期预警 ───────────────────────────────────


async def get_expiring_contracts(
    session: AsyncSession, days: int = 30,
) -> list[ContractResponse]:
    """查询即将到期的合同。"""
    logger.info("查询到期预警 | days={d}", d=days)
    today = date.today()
    deadline = today + timedelta(days=days)
    stmt = (
        select(Contract, Employee.name.label("emp_name"), Department.name.label("dept_name"))
        .outerjoin(Employee, Contract.submitted_by == Employee.id)
        .outerjoin(Department, Contract.department_id == Department.id)
        .where(Contract.status == "approved", Contract.end_date >= today, Contract.end_date <= deadline)
        .order_by(Contract.end_date)
    )
    rows = (await session.execute(stmt)).all()
    return [_contract_to_response(c, en or "", dn or "") for c, en, dn in rows]


# ── 法务人员：条款分析（LLM 辅助） ───────────────────────


async def analyze_contract(
    session: AsyncSession, contract_id: int,
) -> ContractAnalysisResult:
    """对合同进行 LLM 辅助条款分析。"""
    logger.info("合同条款分析 | contract_id={cid}", cid=contract_id)
    c = (await session.execute(select(Contract).where(Contract.id == contract_id))).scalar_one_or_none()
    if not c:
        raise NotFoundException(message="合同不存在")
    if not c.content and not c.key_terms:
        raise BusinessException(message="该合同暂无内容可分析")

    # 组装 prompt
    prompt = f"""请对以下合同进行条款分析，识别关键条款、潜在风险和改进建议。

合同编号：{c.contract_no}
合同标题：{c.title}
合同类型：{c.type}
甲方：{c.party_a}
乙方：{c.party_b}
金额：{float(c.amount)} 元
期限：{c.start_date} 至 {c.end_date}

合同摘要：
{c.content}

关键条款：
{c.key_terms}

请按以下 JSON 格式返回分析结果（纯 JSON，不要包含 markdown 代码块标记）：
{{"summary": "条款摘要", "risks": ["风险点1", "风险点2"], "suggestions": ["建议1", "建议2"]}}"""

    model = get_model()
    response = model.invoke(prompt)

    # 解析 LLM 返回的 JSON
    try:
        content = response.content if hasattr(response, "content") else str(response)
        # 尝试清理可能的 markdown 代码块标记
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        data = json.loads(content)
    except (json.JSONDecodeError, AttributeError):
        data = {
            "summary": str(response.content if hasattr(response, "content") else response),
            "risks": [],
            "suggestions": [],
        }

    return ContractAnalysisResult(
        contract_id=c.id,
        contract_no=c.contract_no,
        summary=data.get("summary", ""),
        risks=data.get("risks", []),
        suggestions=data.get("suggestions", []),
    )


# ── 法务人员：统计报表 ───────────────────────────────────


async def get_contract_stats(session: AsyncSession) -> ContractStatsResponse:
    """合同统计报表。"""
    logger.info("合同统计报表")

    # 总数和总金额
    total_row = (await session.execute(
        select(func.count(), func.coalesce(func.sum(Contract.amount), 0)).select_from(Contract),
    )).one()
    total_count, total_amount = total_row

    # 状态分布
    status_rows = (await session.execute(
        select(Contract.status, func.count()).group_by(Contract.status),
    )).all()
    status_dist = {s: c for s, c in status_rows}

    # 类型分布
    type_rows = (await session.execute(
        select(Contract.type, func.count()).group_by(Contract.type),
    )).all()
    type_dist = {t: c for t, c in type_rows}

    # 即将到期（30 天内）
    today = date.today()
    deadline = today + timedelta(days=30)
    expiring = (await session.execute(
        select(func.count()).select_from(Contract).where(
            Contract.status == "approved", Contract.end_date >= today, Contract.end_date <= deadline,
        ),
    )).scalar_one()

    return ContractStatsResponse(
        total_count=total_count,
        total_amount=round(float(total_amount), 2),
        status_distribution=status_dist,
        type_distribution=type_dist,
        expiring_count=expiring,
    )
