## 1. 数据模型层

- [x] 1.1 创建 `app/models/hr/skill.py` — Skill ORM 模型（employee_id, name, category, level, source, verified）
- [x] 1.2 创建 `app/models/hr/education.py` — Education ORM 模型（employee_id, degree, major, school, graduation_year）
- [x] 1.3 创建 `app/models/hr/project_experience.py` — ProjectExperience ORM 模型（employee_id, project_name, role, start_date, end_date, description, achievement）
- [x] 1.4 创建 `app/models/hr/certificate.py` — Certificate ORM 模型（employee_id, name, issuer, issue_date, expiry_date, category）
- [x] 1.5 更新 `app/models/hr/__init__.py` — 导出 4 个新模型

## 2. Schema 层

- [x] 2.1 在 `app/schemas/hr.py` 新增 SkillResponse / EducationResponse / ProjectExperienceResponse / CertificateResponse
- [x] 2.2 创建 `app/schemas/discovery.py` — 6 个发现场景的响应 Schema（HiddenTalentResult, FlightRiskResult, PromotionReadinessResult, CandidateMatchResult, TalentPortraitResult, TeamCapabilityGapResult）

## 3. Service 层 — 基础 CRUD

- [x] 3.1 在 `app/services/hr.py` 新增 get_employee_skills / get_employee_education / get_employee_projects / get_employee_certificates

## 4. Service 层 — 发现引擎

- [x] 4.1 创建 `app/services/discovery.py` — discover_hidden_talent 规则筛选（绩效轨迹 + 培训统计 + IDP 完成率 + 九宫格标签交叉）
- [x] 4.2 在 discovery.py 新增 assess_flight_risk 规则筛选（高绩效 + 职级停留 + IDP 状态 + 加班趋势）
- [x] 4.3 在 discovery.py 新增 evaluate_promotion_readiness 评估逻辑（综合就绪度评分 1-100）
- [x] 4.4 在 discovery.py 新增 find_candidates 匹配逻辑（技能匹配 + 降级策略）
- [x] 4.5 在 discovery.py 新增 build_talent_portrait 全维度数据汇总
- [x] 4.6 在 discovery.py 新增 analyze_team_capability_gap 团队技能覆盖分析

## 5. Tool 层 — 新模型查询

- [x] 5.1 在 `app/tools/hr/talent_dev_query.py` 新增 td_get_employee_skills / td_get_employee_education / td_get_employee_projects / td_get_employee_certificates

## 6. Tool 层 — 发现工具

- [x] 6.1 创建 `app/tools/hr/discovery.py` — td_discover_hidden_talent Tool
- [x] 6.2 在 discovery.py 新增 td_assess_flight_risk Tool
- [x] 6.3 在 discovery.py 新增 td_promotion_readiness Tool
- [x] 6.4 在 discovery.py 新增 td_find_candidates Tool
- [x] 6.5 在 discovery.py 新增 td_talent_portrait Tool
- [x] 6.6 在 discovery.py 新增 td_team_capability_gap Tool

## 7. 知识库

- [x] 7.1 创建 `app/skills/hr/talent-discovery/references/framework.md` — 人才评估框架（评估维度、分析标准、输出格式指引）

## 8. Agent 集成

- [x] 8.1 更新 `app/agents/hr_agent.py` — 引入 discovery tools + 新模型查询 tools
- [x] 8.2 更新 hr_agent.py instructions — 增加人才发现角色说明和工具使用指引
- [x] 8.3 更新 hr_agent.py skills — 加载 talent-discovery 知识库
