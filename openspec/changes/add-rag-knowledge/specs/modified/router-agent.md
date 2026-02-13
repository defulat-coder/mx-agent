# router-agent

MODIFIED — Router Team 挂载共享 Knowledge Base

## Changes

### CHG-ROUTER-RAG-1: 挂载 Knowledge

`router_team = Team(...)` 新增 `knowledge=company_knowledge` 和 `search_knowledge=True` 参数，使 Router Team 具备文档检索能力。

### CHG-ROUTER-RAG-2: instructions 更新

instructions 新增说明：当用户提问的内容在 Tools 和 Skills 无法覆盖时，Router 应搜索知识库获取企业文档中的相关内容来回答。
