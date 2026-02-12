"""财务智能助手 — 财务相关问答（开发中）"""

from agno.agent import Agent

from app.core.llm import get_model

finance_agent = Agent(
    name="Finance Assistant",
    role="马喜公司财务智能助手",
    model=get_model(),
    instructions=[
        "你是马喜公司的财务智能助手，当前功能正在开发中。",
        "请告知用户：财务助手功能开发中，敬请期待。",
    ],
    markdown=True,
)
