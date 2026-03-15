"""财务智能助手 — 报销管理、预算查询、个税查询、应收应付"""

from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.run import RunContext
from agno.skills import LocalSkills, Skills

from app.core.llm import get_model
from app.tools.finance import fin_admin_tools, fin_employee_tools, fin_manager_tools

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "finance"


def get_finance_tools(run_context: RunContext | None = None, *_, **__) -> list[Callable]:
    """根据用户角色动态返回财务 tools"""
    state = (run_context.session_state if run_context else None) or {}
    roles: list[str] = state.get("roles", [])
    tools = list(fin_employee_tools)  # 所有用户都有基础权限
    if "manager" in roles:
        tools.extend(fin_manager_tools)
    if "finance" in roles:
        tools.extend(fin_admin_tools)
    return tools


finance_agent = Agent(
    id="finance-assistant",
    name="Finance Assistant",
    role="马喜公司财务助手",
    model=get_model(),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    tools=get_finance_tools,
    instructions=[
        """\
你是马喜公司的财务智能助手，服务于当前登录的员工。

## 能力范围
1. **报销查询**：查看报销单列表和详情。
2. **预算查询**：查看部门当年预算余额。
3. **个税查询**：查看个人所得税明细（近 3 个月或指定月份）。
4. **制度咨询**：报销标准、预算制度、个税计算规则。优先使用 Skills 获取准确制度内容后回答，不要编造。

## 行为准则
- 涉及具体数据时必须调用 Tool，不要猜测或编造数据。
- 报销金额、预算金额等财务数据需准确展示，不要四舍五入。
- 个税问题优先查阅 tax-knowledge Skill，报销问题优先查阅 reimbursement-policy Skill。
- 超出财务范围的问题，礼貌告知不在服务范围内，建议联系相关部门。
- 回答简洁、准确，使用中文。
""",
    ],
    markdown=True,
)
