"""财务人员操作 Tools — 报销审核、开票处理"""

import json

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import finance as fin_service
from app.tools.finance.utils import get_finance_id


async def fin_admin_review_reimbursement(
    run_context: RunContext,
    reimbursement_id: int,
    action: str,
    remark: str = "",
) -> str:
    """审核报销单：approve 通过（自动扣减预算）/ reject 拒绝 / return 退回。

    Args:
        reimbursement_id: 报销单 ID
        action: 操作（approve/reject/return）
        remark: 审核备注
    """
    logger.info("tool=fin_admin_review_reimbursement | id={rid} action={act}", rid=reimbursement_id, act=action)
    try:
        admin_id = get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            record = await fin_service.review_reimbursement(session, reimbursement_id, admin_id, action, remark)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def fin_admin_process_invoice_request(
    run_context: RunContext,
    customer: str,
    amount: float,
    description: str = "",
) -> str:
    """处理开票申请。返回开票结果（模拟）。

    Args:
        customer: 客户名称
        amount: 开票金额
        description: 开票说明
    """
    logger.info("tool=fin_admin_process_invoice_request | customer={c} amount={a}", c=customer, a=amount)
    try:
        get_finance_id(run_context)
    except ValueError as e:
        return str(e)
    result = {
        "status": "success",
        "message": f"已为 {customer} 开具金额 {amount:.2f} 元的发票",
        "invoice_url": f"https://oa.maxi.com/invoice/preview?customer={customer}&amount={amount}",
    }
    return json.dumps(result, ensure_ascii=False)
