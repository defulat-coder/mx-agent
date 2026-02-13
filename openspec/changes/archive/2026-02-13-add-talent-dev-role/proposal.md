## Why

HR Agent 已实现员工、主管、管理者三个角色，覆盖了日常事务查询和审批场景。但缺少面向 HRBP/人才发展专员的分析洞察能力——培训管理、人才盘点（九宫格）、个人发展计划（IDP）等人才发展核心场景无法支撑。需要新增「人才发展」角色，补齐组织健康度和人才成长维度的能力。

## What Changes

- 新增 3 个数据模型：`Training`（培训记录/计划合并）、`TalentReview`（人才盘点九宫格）、`DevelopmentPlan`（个人发展计划 IDP）
- 新增种子数据脚本，为 3 张新表生成模拟数据
- 新增 `talent_dev` 角色标识，全公司只读权限（含薪资、社保、绩效评语）
- 新增 7 个个人数据查询 Tool：员工档案、培训记录、盘点结果、IDP、绩效详情、岗位履历、考勤
- 新增 6 个分析报表 Tool：培训完成率、九宫格分布、绩效分布趋势、人员流动分析、晋升统计、IDP 达成率
- HR Agent instructions 增加人才发展角色说明
- 模拟员工数据增加一个 `talent_dev` 角色用户

## Capabilities

### New Capabilities
- `talent-dev-models`: 培训、人才盘点、IDP 三个数据模型定义及种子数据
- `talent-dev-tools`: 人才发展角色的 13 个只读查询/报表 Tool

### Modified Capabilities
- `hr-agent-impl`: 增加 talent_dev 角色权限说明和工具注册

## Impact

- 新增文件：`app/models/hr/training.py`、`app/models/hr/talent_review.py`、`app/models/hr/development_plan.py`、`app/tools/hr/talent_dev_query.py`
- 修改文件：`app/models/hr/__init__.py`、`app/schemas/hr.py`、`app/services/hr.py`、`app/tools/hr/utils.py`、`app/tools/hr/__init__.py`、`app/agents/hr_agent.py`、`scripts/generate_seed.py`
- 需要重建数据库（新增 3 张表 + 种子数据）
