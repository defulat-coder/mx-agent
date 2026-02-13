## Context

当前 `legal_agent.py` 为占位 Agent，仅返回"功能开发中"。需替换为完整法务助手，覆盖合同模板查询、合同管理、审查、到期预警、LLM 条款分析。复用现有 JWT + RBAC + SQLite + Agno 架构。

## Goals / Non-Goals

**Goals:**
- 3 张表覆盖合同模板 + 合同 + 审查记录
- 员工 3 工具 + 法务人员 5 工具 = 8 个 Tools
- 3 个 Skills 知识库（劳动法 / 合同知识 / 合规知识）
- LLM 辅助的合同条款分析
- `legal` 角色权限控制

**Non-Goals:**
- 不做诉讼/纠纷管理（LegalCase）
- 不做合规培训表（用 Skills 替代）
- 不做合同文件上传/存储（模板下载返回 OA 链接）

## Decisions

### D1: 数据模型 — 3 张表

| 表 | 关键字段 | 说明 |
|---|---|---|
| `ContractTemplate` | name, type, description, file_url | 合同模板，file_url 存 OA 下载链接 |
| `Contract` | contract_no, title, type, party_a, party_b, amount, start_date, end_date, status, content, key_terms, submitted_by(FK), department_id(FK) | 合同记录，content 存合同摘要/关键内容，key_terms 存 JSON 格式关键条款 |
| `ContractReview` | contract_id(FK), reviewer_id(FK), action(approved/returned), opinion | 审查记录 |

选择在 Contract 表存 `content`（合同摘要文本）和 `key_terms`（JSON 关键条款），供 LLM 条款分析使用，无需单独文件存储。

### D2: 条款分析实现 — Agent 内 LLM 调用

`leg_admin_analyze_contract` 工具实现：
1. 从 DB 读取 Contract 的 content + key_terms
2. 组装 prompt（包含合同类型、条款内容）
3. 调用 `get_model()` 生成分析结果（关键条款摘要 + 风险点 + 建议）
4. 返回结构化 JSON

不做独立的分析模型/服务，直接在 tool 函数中调用 LLM。

### D3: 工具命名与分组

| 前缀 | 角色 | 工具 |
|---|---|---|
| `leg_` | 员工 | `leg_get_templates`, `leg_get_template_download`, `leg_get_my_contracts` |
| `leg_admin_` | 法务人员 | `leg_admin_get_contracts`, `leg_admin_review_contract`, `leg_admin_get_expiring`, `leg_admin_analyze_contract`, `leg_admin_get_stats` |

导出：`leg_employee_tools`（3 个）+ `leg_admin_tools`（5 个）

### D4: Skills 知识库

| Skill 目录 | 内容 |
|---|---|
| `app/skills/legal/labor-law/` | 劳动合同法、试用期、解雇保护、经济补偿 |
| `app/skills/legal/contract-knowledge/` | 合同签订流程、竞业限制、保密协议、知识产权 |
| `app/skills/legal/compliance/` | 企业合规要求、反腐败、数据隐私、审计配合 |

### D5: legal 角色

复用现有 RBAC 模式：
- `_MOCK_EMPLOYEES` 中给郑晓明追加 `legal` 角色
- `generate_token.py` 的 manager 用户追加 `legal`
- `app/tools/legal/utils.py` 提供 `get_legal_id`

### D6: Mock 数据量

| 表 | 数量 |
|---|---|
| ContractTemplate | ~10 |
| Contract | ~60 |
| ContractReview | ~30 |

## Risks / Trade-offs

- [条款分析依赖 LLM 质量] → 返回结果加 disclaimer 提示"仅供参考，不构成法律意见"
- [Contract.content 文本长度] → Mock 数据中仅存摘要级内容（200-500 字），实际使用时可扩展
- [key_terms 存 JSON 字符串] → SQLite 无 JSON 字段类型，用 Text 存储，Python 侧 json.loads 解析
