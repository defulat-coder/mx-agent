"""智能助手路由组 — 将用户请求分发到 HR/IT/行政/财务/法务子助手"""

import json

from agno.run import RunContext
from agno.team.team import Team

from app.agents.admin_agent import admin_agent
from app.agents.finance_agent import finance_agent
from app.agents.hr_agent import hr_agent
from app.agents.it_agent import it_agent
from app.agents.legal_agent import legal_agent
from app.core.database import async_session_factory
from app.core.llm import get_model
from app.services import hr as hr_service
from app.tools.hr.utils import get_employee_id


async def get_current_user(run_context: RunContext) -> str:
    """获取当前登录用户的基本信息和角色权限（姓名、工号、部门、岗位、职级、入职日期、状态、角色）"""
    employee_id = get_employee_id(run_context)
    state = run_context.session_state
    roles: list[str] = state.get("roles", []) if state else []  # type: ignore[union-attr]
    async with async_session_factory() as session:
        info = await hr_service.get_employee_info(session, employee_id)
        data = info.model_dump()
        data["roles"] = roles
        return json.dumps(data, ensure_ascii=False, default=str)


router_team = Team(
    id="router-team",
    name="马喜智能助手",
    model=get_model(),
    respond_directly=True,
    add_history_to_context=True,
    num_history_runs=5,
    enable_agentic_memory=True,
    members=[hr_agent, it_agent, admin_agent, finance_agent, legal_agent],
    tools=[get_current_user],
    instructions=[
        "你是马喜公司的智能助手入口，负责将用户请求路由到合适的子助手。",
        "当用户询问「我是谁」或需要了解自己身份信息时，调用 get_current_user 工具直接回答。",
        "HR 相关问题（考勤、请假、薪资、社保、入离职、报销、培训等）→ HR Assistant",
        "IT 运维相关问题（设备报修、密码重置、权限申请、软件安装、设备查询、WiFi/VPN/打印机问题等）→ IT Assistant",
        "行政相关问题（会议室预订、办公用品申领、快递收发、访客预约、差旅申请、办公规范等）→ Admin Assistant",
        "财务相关问题（报销查询、预算管理、个税查询、费用汇总、应收应付等）→ Finance Assistant",
        "法务相关问题（合同查询、合同模板、合同审查、法律咨询、合规问题等）→ Legal Assistant",
        "如果无法判断归属，友好告知用户当前支持的功能范围。",
    ],
    markdown=True,
    show_members_responses=True,
)
