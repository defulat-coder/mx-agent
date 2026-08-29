"""财务人员操作 Tools — 报销审核、开票处理"""

import json
from urllib.parse import urlencode

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.core.exceptions import AppException
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
        except AppException as e:
            return e.message
        except Exception:
            logger.exception("报销审核失败 | reimbursement_id={rid}", rid=reimbursement_id)
            return "服务内部错误，请稍后重试"


async def fin_admin_process_invoice_request(
    run_context: RunContext,
    customer: str,
    amount: float,
    description: str = "",
) -> str:
    """准备开票申请链接，需用户在 OA 页面确认后提交。

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
    if not customer.strip() or amount <= 0:
        return "客户名称不能为空，且开票金额必须大于 0"
    query = urlencode({"customer": customer.strip(), "amount": f"{amount:.2f}", "description": description})
    result = {
        "status": "prepared",
        "requires_user_action": True,
        "message": "开票信息已准备，请在 OA 页面核对并提交",
        "invoice_url": f"https://oa.maxi.com/invoice/preview?{query}",
    }
    return json.dumps(result, ensure_ascii=False)
