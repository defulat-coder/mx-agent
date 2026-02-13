## 1. 数据模型

- [x] 1.1 创建 `app/models/legal/contract_template.py` — ContractTemplate 模型
- [x] 1.2 创建 `app/models/legal/contract.py` — Contract 模型（含 content/key_terms Text 字段）
- [x] 1.3 创建 `app/models/legal/contract_review.py` — ContractReview 模型
- [x] 1.4 创建 `app/models/legal/__init__.py` — 导出全部 3 个模型
- [x] 1.5 创建 `app/schemas/legal.py` — Pydantic Schema（含 ContractAnalysisResult）

## 2. Service 层

- [x] 2.1 创建 `app/services/legal.py` — 实现全部业务逻辑方法
- [x] 2.2 实现 get_templates / get_template_detail 查询
- [x] 2.3 实现 get_my_contracts（按 submitted_by 过滤）
- [x] 2.4 实现 get_all_contracts（多条件筛选）
- [x] 2.5 实现 review_contract（更新状态 + 创建 ContractReview）
- [x] 2.6 实现 get_expiring_contracts（到期预警，默认 30 天）
- [x] 2.7 实现 analyze_contract（读取合同内容，调 LLM 返回分析结果）
- [x] 2.8 实现 get_contract_stats（统计报表）

## 3. Tools 层

- [x] 3.1 创建 `app/tools/legal/utils.py` — get_legal_id 角色校验
- [x] 3.2 创建 `app/tools/legal/query.py` — 员工工具：leg_get_templates, leg_get_template_download, leg_get_my_contracts
- [x] 3.3 创建 `app/tools/legal/admin_query.py` — 法务人员查询：leg_admin_get_contracts, leg_admin_get_expiring, leg_admin_get_stats
- [x] 3.4 创建 `app/tools/legal/admin_action.py` — 法务人员操作：leg_admin_review_contract, leg_admin_analyze_contract
- [x] 3.5 创建 `app/tools/legal/__init__.py` — 导出 leg_employee_tools + leg_admin_tools

## 4. Skills 知识库

- [x] 4.1 创建 `app/skills/legal/labor-law/` — SKILL.md + references/policy.md
- [x] 4.2 创建 `app/skills/legal/contract-knowledge/` — SKILL.md + references/policy.md
- [x] 4.3 创建 `app/skills/legal/compliance/` — SKILL.md + references/policy.md

## 5. Agent 集成

- [x] 5.1 替换 `app/agents/legal_agent.py` — 完整 Agent 定义（8 工具 + 3 Skills）
- [x] 5.2 更新 `app/agents/router_agent.py` — 法务路由规则细化
- [x] 5.3 更新 `app/core/database.py` — init_db 导入 app.models.legal

## 6. 角色与权限

- [x] 6.1 更新 `app/tools/hr/utils.py` — 郑晓明 _MOCK_EMPLOYEES 追加 legal
- [x] 6.2 更新 `scripts/generate_token.py` — manager 用户追加 legal

## 7. Mock 数据

- [x] 7.1 创建 `scripts/seed_legal_data.py` — 生成 ~100 条 Mock 数据
- [x] 7.2 执行脚本生成 `scripts/legal_seed.sql`
- [x] 7.3 灌入数据库并验证记录数
