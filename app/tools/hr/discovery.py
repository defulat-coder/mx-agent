"""人才发现 Tools — 6 个发现场景（只读分析）"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import discovery as discovery_service
from app.tools.hr.utils import get_talent_dev_id
from loguru import logger


async def td_discover_hidden_talent(
    run_context: RunContext,
    department_id: int | None = None,
) -> str:
    """识别被埋没的高潜人才：绩效优秀 + 培训活跃 + IDP 完成率高，但九宫格标签低估的员工。可按部门过滤。"""
    logger.info("tool=td_discover_hidden_talent | department_id={department_id}", department_id=department_id)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.discover_hidden_talent(session, department_id)
        return result.model_dump_json()


async def td_assess_flight_risk(
    run_context: RunContext,
    department_id: int | None = None,
) -> str:
    """流失风险预警：识别高绩效但有流失风险的员工（职级停滞 + 发展停滞）。可按部门过滤。"""
    logger.info("tool=td_assess_flight_risk | department_id={department_id}", department_id=department_id)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.assess_flight_risk(session, department_id)
        return result.model_dump_json()


async def td_promotion_readiness(
    run_context: RunContext,
    employee_id: int | None = None,
    department_id: int | None = None,
) -> str:
    """晋升准备度评估：综合职级停留、绩效、管理培训、IDP 进度，输出 1-100 就绪度评分。传 employee_id 评估单人，传 department_id 评估部门全员。"""
    logger.info("tool=td_promotion_readiness | employee_id={employee_id} department_id={department_id}", employee_id=employee_id, department_id=department_id)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.evaluate_promotion_readiness(
            session, employee_id, department_id,
        )
        return result.model_dump_json()


async def td_find_candidates(
    run_context: RunContext,
    requirements: str,
) -> str:
    """岗位适配推荐：根据技能要求描述推荐匹配人选。requirements 为逗号分隔的技能/能力关键词，如"Python,项目管理,数据分析"。"""
    logger.info("tool=td_find_candidates | requirements={requirements}", requirements=requirements)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.find_candidates(session, requirements)
        return result.model_dump_json()


async def td_talent_portrait(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """生成员工完整人才画像：汇总基本信息、教育、技能、项目、证书、绩效、培训、IDP、九宫格、岗位变动等全维度数据。"""
    logger.info("tool=td_talent_portrait | employee_id={employee_id}", employee_id=employee_id)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.build_talent_portrait(session, employee_id)
        return result.model_dump_json()


async def td_team_capability_gap(
    run_context: RunContext,
    department_id: int,
) -> str:
    """团队能力短板分析：分析指定部门的技能覆盖度、高频技能、稀缺技能和能力缺口。"""
    logger.info("tool=td_team_capability_gap | department_id={department_id}", department_id=department_id)
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await discovery_service.analyze_team_capability_gap(session, department_id)
        return result.model_dump_json()
