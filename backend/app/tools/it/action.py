"""IT 员工操作 Tools — 创建工单"""

from agno.run import RunContext
from loguru import logger

from app.core.database import async_session_factory
from app.services import it as it_service
from app.tools.hr.utils import get_employee_id


async def it_create_ticket(
    run_context: RunContext,
    type: str,
    title: str,
    description: str = "",
    priority: str = "medium",
) -> str:
    """创建 IT 工单（报修、密码重置、软件安装、权限申请等）。

    Args:
        type: 工单类型（repair/password_reset/software_install/permission/other）
        title: 工单标题
        description: 问题描述
        priority: 优先级（low/medium/high/urgent），默认 medium
    """
    logger.info("tool=it_create_ticket | type={type} priority={priority}", type=type, priority=priority)
    employee_id = get_employee_id(run_context)
    async with async_session_factory() as session:
        record = await it_service.create_ticket(session, employee_id, type, title, description, priority)
        await session.commit()
        return record.model_dump_json()
