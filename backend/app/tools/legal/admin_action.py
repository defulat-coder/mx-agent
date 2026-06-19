"""法务人员操作 Tools — 合同审查、条款分析"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import legal as legal_service
from app.tools.legal.utils import get_legal_id


async def leg_admin_review_contract(
    run_context: RunContext,
    contract_id: int,
    action: str,
    opinion: str = "",
) -> str:
    """审查合同：approved 通过 / returned 退回。

    Args:
        contract_id: 合同 ID
        action: 操作（approved/returned）
        opinion: 审查意见
    """
    logger.info("tool=leg_admin_review_contract | id={cid} action={act}", cid=contract_id, act=action)
    try:
        reviewer_id = get_legal_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            record = await legal_service.review_contract(session, contract_id, reviewer_id, action, opinion)
            await session.commit()
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def leg_admin_analyze_contract(
    run_context: RunContext,
    contract_id: int,
) -> str:
    """对合同进行 LLM 辅助条款分析（关键条款提取、风险识别、改进建议）。

    Args:
        contract_id: 合同 ID
    """
    logger.info("tool=leg_admin_analyze_contract | id={cid}", cid=contract_id)
    try:
        get_legal_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        try:
            result = await legal_service.analyze_contract(session, contract_id)
            return result.model_dump_json()
        except Exception as e:
            return str(e)
