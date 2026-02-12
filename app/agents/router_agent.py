"""智能助手路由组 — 将用户请求分发到 HR/财务/法务子助手"""

from agno.team.team import Team

from app.agents.finance_agent import finance_agent
from app.agents.hr_agent import hr_agent
from app.agents.legal_agent import legal_agent
from app.core.llm import get_model

router_team = Team(
    id="router-team",
    name="马喜智能助手",
    model=get_model(),
    respond_directly=True,
    enable_agentic_memory=True,
    members=[hr_agent, finance_agent, legal_agent],
    instructions=[
        "你是马喜公司的智能助手入口，负责将用户请求路由到合适的子助手。",
        "HR 相关问题（考勤、请假、薪资、社保、入离职、报销、培训等）→ HR Assistant",
        "财务相关问题 → Finance Assistant",
        "法务相关问题 → Legal Assistant",
        "如果无法判断归属，友好告知用户当前支持的功能范围。",
    ],
    markdown=True,
    show_members_responses=True,
)
