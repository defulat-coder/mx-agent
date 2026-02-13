## Why

法务助手是企业智能助手最后一个待实现的业务域。当前 `legal_agent.py` 仅为占位，员工无法查询合同模板、跟踪审批进度；法务人员缺乏合同管理、审查、到期预警和条款分析能力。上线后可覆盖合同全生命周期管理。

## What Changes

- 替换 `legal_agent.py` 占位，实现完整法务 Agent（8 个 Tools + 3 个 Skills）
- 新增 3 张 ORM 表：`ContractTemplate`、`Contract`、`ContractReview`
- 新增 `legal` 角色，法务人员可管理全公司合同
- 员工工具 3 个：查模板、获取模板下载链接、查合同审批进度
- 法务人员工具 5 个：合同台账、合同审查、到期预警、条款分析（LLM 辅助）、统计报表
- 3 个 Skills 知识库：劳动法、合同知识、合规知识
- ~100 条 Mock 数据
- Router Team 路由规则更新

## Capabilities

### New Capabilities
- `legal-data-models`: 法务数据模型（3 张表 + Pydantic Schema）
- `legal-query-tools`: 员工 + 法务人员查询工具
- `legal-action-tools`: 法务人员操作工具（审查 + 条款分析）
- `legal-agent-impl`: Agent 定义、Skills 知识库、工具导出

### Modified Capabilities
- `auth`: 新增 `legal` 角色到 mock 用户和 JWT，新增 `get_legal_id`
- `router-agent`: 法务路由从"功能开发中"改为具体描述
- `database`: `init_db` 导入法务模型

## Impact

- 新增文件：`app/models/legal/`、`app/schemas/legal.py`、`app/services/legal.py`、`app/tools/legal/`、`app/skills/legal/`
- 修改文件：`app/agents/legal_agent.py`、`app/agents/router_agent.py`、`app/core/database.py`、`app/tools/hr/utils.py`、`scripts/generate_token.py`
- 条款分析工具需调用 LLM（复用 `app/core/llm.py` 的 `get_model()`）
