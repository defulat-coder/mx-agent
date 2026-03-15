"""HR 智能助手 — 考勤、薪资、社保、入离职等 HR 相关问答与业务办理"""

from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.run import RunContext
from agno.skills import LocalSkills, Skills

from app.core.llm import get_model
from app.tools.hr import admin_tools, discovery_tools, employee_tools, manager_tools, talent_dev_tools

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "hr"


def get_hr_tools(run_context: RunContext | None = None, *_, **__) -> list[Callable]:
    """根据用户角色动态返回 HR tools"""
    state = (run_context.session_state if run_context else None) or {}
    roles: list[str] = state.get("roles", [])
    tools = list(employee_tools)  # 所有用户都有基础权限
    if "manager" in roles:
        tools.extend(manager_tools)
    if "admin" in roles:
        tools.extend(admin_tools)
    if "talent_dev" in roles:
        tools.extend(talent_dev_tools)
        tools.extend(discovery_tools)
    return tools


hr_agent = Agent(
    id="hr-assistant",
    name="HR Assistant",
    role="马喜公司 HR 助手",
    model=get_model(),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    tools=get_hr_tools,
    instructions=[
        """\
你是马喜公司的 HR 员工智能助手，服务于当前登录的员工。

## 能力范围
1. **制度咨询**：考勤、假期、薪酬、社保公积金、入职、离职、报销、培训等公司制度政策。优先使用 Skills 获取准确的制度内容后回答，不要编造。
2. **数据查询**：员工个人信息、薪资明细、社保缴纳、考勤记录、假期余额、请假记录、加班记录。调用对应 Tool 获取真实数据后回答。
3. **业务办理**：请假申请、加班登记、报销申请。收集必要信息后调用 Action Tool，将审批链接提供给员工。
4. **人才发现分析（talent_dev 角色）**：当用户提出人才分析诉求时，根据意图选择 discovery tools：离职风险→`td_assess_flight_risk`，晋升准备度→`td_promotion_readiness`，人岗匹配候选→`td_find_candidates`，个体画像→`td_talent_portrait`，高潜识别→`td_discover_hidden_talent`，团队能力差距→`td_team_capability_gap`。

## 行为准则
- 涉及具体数据时必须调用 Tool，不要猜测或编造数据。
- 涉及业务办理时，确认收集齐必要信息再调用 Action Tool。
- 审批前应先查看待审批列表确认信息，再执行审批操作。
- discovery tools 返回后，按“结论-依据-建议”结构输出，避免仅回传原始数据。
- 超出 HR 服务范围的问题，礼貌告知不在服务范围内，建议联系相关部门。
- 回答简洁、准确，使用中文。
""",
    ],
    markdown=True,
)
