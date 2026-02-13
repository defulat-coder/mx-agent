## Why

当前 HR 系统的人才盘点依赖人工标记（九宫格标签由主管手动填写），系统仅提供"记录与查阅"功能，无法主动发现被埋没的高潜人才、预警流失风险或推荐岗位适配人选。需要构建数据驱动的人才发现引擎，让系统从"被动查人"升级为"主动找人"。

## What Changes

- 新增 4 个数据模型：技能标签（Skill）、教育背景（Education）、项目经历（ProjectExperience）、证书认证（Certificate），补齐人才画像的关键数据维度
- 新增 6 个人才发现 Tool：被埋没高潜识别、流失风险预警、晋升准备度评估、岗位适配推荐、完整人才画像、团队能力短板分析
- 采用混合分析模式：规则引擎筛选候选人 + LLM 生成综合分析报告与建议
- 新增人才评估框架知识库（Skill），指导 LLM 进行人才分析时的评估标准
- 扩展现有 talent_dev 查询工具，支持新增 4 个模型的数据查询

## Capabilities

### New Capabilities
- `talent-data-models`: 新增 Skill / Education / ProjectExperience / Certificate 四个 ORM 模型及对应 Schema、Service CRUD
- `talent-discovery-engine`: 6 个人才发现场景 Tool（混合模式：规则筛选 + LLM 分析）及底层分析服务

### Modified Capabilities
- `hr-query-tools`: 新增 4 个模型的 talent_dev 查询 Tool（td_get_employee_skills / td_get_employee_education / td_get_employee_projects / td_get_employee_certificates）
- `hr-agent-impl`: 引入 discovery tools，更新 instructions 增加人才发现角色说明

## Impact

- **数据库**: 新增 4 张表（skills / educations / project_experiences / certificates），自动建表
- **模型层**: `app/models/hr/` 新增 4 个文件
- **Schema 层**: `app/schemas/` 新增 discovery.py，修改 hr.py
- **服务层**: `app/services/` 新增 discovery.py，修改 hr.py
- **工具层**: `app/tools/hr/` 新增 discovery.py，修改 talent_dev_query.py
- **智能体**: `app/agents/hr_agent.py` 引入新工具并更新指令
- **知识库**: `app/skills/hr/` 新增 talent-discovery 目录
