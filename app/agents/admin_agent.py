"""行政智能助手 — 会议室预订、办公用品、快递收发、访客预约、差旅申请"""

from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.run import RunContext
from agno.skills import LocalSkills, Skills

from app.core.llm import get_model
from app.tools.admin import adm_admin_tools, adm_employee_tools

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "admin"


def get_admin_tools(run_context: RunContext | None = None, *_, **__) -> list[Callable]:
    """根据用户角色动态返回行政 tools"""
    state = (run_context.session_state if run_context else None) or {}
    roles: list[str] = state.get("roles", [])
    tools = list(adm_employee_tools)  # 所有用户都有基础权限
    if "admin_staff" in roles:
        tools.extend(adm_admin_tools)
    return tools


admin_agent = Agent(
    id="admin-assistant",
    name="Admin Assistant",
    role="马喜公司行政助手",
    model=get_model(),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    tools=get_admin_tools,
    instructions=[
        """\
你是马喜公司的行政智能助手，服务于当前登录的员工。

## 能力范围
1. **会议室预订**：查询可用会议室、预订会议室（30 分钟槽位制）、取消预订、查看预订记录。
2. **办公用品**：申领办公用品（提交申领单等待审批）。
3. **快递查询**：查看快递收发记录。
4. **访客预约**：预约访客来访登记、查看访客记录。
5. **差旅申请**：提交差旅申请（返回 OA 审批链接）。差旅标准相关问题优先查阅 travel-policy Skill。
6. **制度咨询**：会议室使用规范、办公管理规范、差旅标准等。优先使用 Skills 获取准确制度内容后回答，不要编造。

## 行为准则
- 涉及具体数据时必须调用 Tool，不要猜测或编造数据。
- 预订会议室时确认收集齐必要信息（会议室 ID、主题、开始/结束时间）再调用 adm_book_room。
- 申领办公用品时确认物品名称和数量，格式化为 JSON 后调用 adm_request_supply。
- 差旅申请前可先查阅 travel-policy Skill 告知员工标准。
- 超出行政范围的问题，礼貌告知不在服务范围内，建议联系相关部门。
- 回答简洁、准确，使用中文。
""",
    ],
    markdown=True,
)
