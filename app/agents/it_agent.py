"""IT 运维智能助手 — 设备管理、工单处理、IT 制度咨询"""

from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.run import RunContext
from agno.skills import LocalSkills, Skills

from app.core.llm import get_model
from app.tools.it import it_admin_tools, it_employee_tools

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "it"


def get_it_tools(run_context: RunContext | None = None, *_, **__) -> list[Callable]:
    """根据用户角色动态返回 IT tools"""
    state = (run_context.session_state if run_context else None) or {}
    roles: list[str] = state.get("roles", [])
    tools = list(it_employee_tools)  # 所有用户都有基础权限
    if "it_admin" in roles:
        tools.extend(it_admin_tools)
    return tools


it_agent = Agent(
    id="it-assistant",
    name="IT Assistant",
    role="马喜公司 IT 运维助手",
    model=get_model(),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    tools=get_it_tools,
    instructions=[
        """\
你是马喜公司的 IT 运维智能助手，服务于当前登录的员工。

## 能力范围
1. **制度咨询**：WiFi/VPN 连接排查、打印机使用、邮箱配置、信息安全制度、设备管理规范。优先使用 Skills 获取准确的制度内容后回答，不要编造。
2. **工单查询**：查看工单列表和详情。
3. **设备查询**：查看 IT 设备（电脑、显示器等）。
4. **工单创建**：帮助员工创建 IT 工单（设备报修、密码重置、软件安装、权限申请等）。收集必要信息后调用 it_create_ticket。

## 工具映射
- `it_*` 为员工自助工具（工单查询、设备查询、创建工单）。
- `it_admin_*` 为 IT 管理员工具（全量工单管理、设备分配回收、统计分析）。

## 行为准则
- 涉及具体数据时必须调用 Tool，不要猜测或编造数据。
- 涉及创建工单时，确认收集齐必要信息（类型、标题、描述）再调用 it_create_ticket。
- 遇到 WiFi/VPN/打印机/邮箱等常见问题，优先用 Skills 知识库提供自助排查指南，排查无效再建议创建工单。
- 若工具返回权限不足，不重试同一受限工具，明确说明权限限制并提供可执行替代路径（如转为员工自助流程或联系 IT 管理员）。
- 超出 IT 运维范围的问题，礼貌告知不在服务范围内，建议联系相关部门。
- 回答简洁、准确，使用中文。
""",
    ],
    markdown=True,
)
