"""法务员工查询 Tools — 合同模板查询、模板下载、合同进度查询"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import legal as legal_service
from app.tools.hr.utils import get_employee_id


async def leg_get_templates(run_context: RunContext, type: str | None = None) -> str:
    """查询合同模板列表。可选按类型筛选（劳动合同/保密协议/采购合同/销售合同/服务合同/其他）。

    Args:
        type: 合同类型筛选，不传则返回全部
    """
    logger.info("tool=leg_get_templates | type={t}", t=type)
    async with async_session_factory() as session:
        records = await legal_service.get_templates(session, type)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def leg_get_template_download(run_context: RunContext, template_id: int) -> str:
    """获取合同模板下载链接。返回模板信息和 OA 下载地址。

    Args:
        template_id: 模板 ID
    """
    logger.info("tool=leg_get_template_download | id={tid}", tid=template_id)
    async with async_session_factory() as session:
        try:
            record = await legal_service.get_template_detail(session, template_id)
            return record.model_dump_json()
        except Exception as e:
            return str(e)


async def leg_get_my_contracts(run_context: RunContext, status: str | None = None) -> str:
    """查询我提交的合同审批进度。可选按状态筛选（draft/pending/approved/rejected/returned/expired/terminated）。

    Args:
        status: 合同状态筛选，不传则返回全部
    """
    logger.info("tool=leg_get_my_contracts | status={s}", s=status)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        records = await legal_service.get_my_contracts(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"
