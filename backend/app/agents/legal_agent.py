"""法务智能助手 — 合同管理、法律咨询、合规知识"""

from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.run import RunContext
from agno.skills import LocalSkills, Skills

from app.core.llm import get_model
from app.tools.legal import leg_admin_tools, leg_employee_tools

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "legal"


def get_legal_tools(run_context: RunContext | None = None, *_, **__) -> list[Callable]:
    """根据用户角色动态返回法务 tools"""
    state = (run_context.session_state if run_context else None) or {}
    roles: list[str] = state.get("roles", [])
    tools = list(leg_employee_tools)  # 所有用户都有基础权限
    if "legal" in roles:
        tools.extend(leg_admin_tools)
    return tools


legal_agent = Agent(
    id="legal-assistant",
    name="Legal Assistant",
    role="马喜公司法务助手",
    model=get_model(),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    tools=get_legal_tools,
    instructions=[
        """\
你是马喜公司的法务智能助手，服务于当前登录的员工。

## 能力范围
1. **合同模板查询**：查看各类合同模板列表，获取模板下载链接。
2. **合同进度查询**：查看合同审批进度。
3. **法律咨询**：劳动法、竞业限制、保密协议、知识产权等问题。优先使用 Skills 获取准确制度内容后回答，不要编造。
4. **合规咨询**：企业合规要求、反腐败、数据隐私、审计配合等问题。

## 行为准则
- 涉及具体数据时必须调用 Tool，不要猜测或编造数据。
- 法律咨询优先查阅 labor-law / contract-knowledge / compliance Skill。
- 条款分析结果需附带免责声明：“以上分析仅供参考，不构成法律意见。具体法律事务请咨询专业律师。”
- 超出法务范围的问题，礼貌告知不在服务范围内，建议联系相关部门。
- 回答简洁、准确，使用中文。
""",
    ],
    markdown=True,
)
