"""法务智能助手 — 法务相关问答（开发中）"""

from agno.agent import Agent

from app.core.llm import get_model

legal_agent = Agent(
    name="Legal Assistant",
    role="马喜公司法务智能助手",
    model=get_model(),
    instructions=[
        "你是马喜公司的法务智能助手，当前功能正在开发中。",
        "请告知用户：法务助手功能开发中，敬请期待。",
    ],
    markdown=True,
)
