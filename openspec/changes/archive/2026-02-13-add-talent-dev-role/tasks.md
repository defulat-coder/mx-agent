## 1. 数据模型

- [x] 1.1 新建 `app/models/hr/training.py` — Training ORM 模型
- [x] 1.2 新建 `app/models/hr/talent_review.py` — TalentReview ORM 模型
- [x] 1.3 新建 `app/models/hr/development_plan.py` — DevelopmentPlan ORM 模型
- [x] 1.4 更新 `app/models/hr/__init__.py` — 导出 3 个新模型

## 2. 种子数据

- [x] 2.1 更新 `scripts/generate_seed.py` — 为 trainings/talent_reviews/development_plans 3 张表生成模拟数据，确保与现有员工和绩效数据自洽

## 3. Schemas

- [x] 3.1 更新 `app/schemas/hr.py` — 新增 Training/TalentReview/DevelopmentPlan 响应 Schema
- [x] 3.2 更新 `app/schemas/hr.py` — 新增 6 个报表汇总 Schema（TrainingSummary/NineGridDistribution/PerformanceDistribution/TurnoverAnalysis/PromotionStats/IdpSummary）

## 4. Service 层

- [x] 4.1 更新 `app/services/hr.py` — 新增 7 个人才发展个人查询 service 函数
- [x] 4.2 更新 `app/services/hr.py` — 新增 6 个报表汇总 service 函数

## 5. 身份提取

- [x] 5.1 更新 `app/tools/hr/utils.py` — 新增 `get_talent_dev_id()` 函数
- [x] 5.2 更新 `app/tools/hr/utils.py` — `_MOCK_EMPLOYEES` 增加一个 talent_dev 角色用户

## 6. Tools 层

- [x] 6.1 新建 `app/tools/hr/talent_dev_query.py` — 7 个个人数据查询 Tool + 6 个报表 Tool
- [x] 6.2 更新 `app/tools/hr/__init__.py` — 导出 `talent_dev_tools` 并合入 `all_tools`

## 7. Agent 指令

- [x] 7.1 更新 `app/agents/hr_agent.py` — tools 列表增加 `talent_dev_tools`，instructions 增加人才发展角色说明

## 8. 数据库重建与验证

- [x] 8.1 删除旧数据库，重新执行种子脚本生成新数据
- [x] 8.2 重启服务，验证启动无报错
