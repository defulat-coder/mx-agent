## ADDED Requirements

### Requirement: 被埋没高潜识别
系统 SHALL 提供 td_discover_hidden_talent Tool，基于多维数据交叉分析识别被低估的高潜人才。

#### Scenario: 发现被埋没的高潜员工
- **WHEN** 调用 td_discover_hidden_talent(department_id=可选)
- **THEN** 返回符合条件的候选人列表：绩效连续 2 期 >= B+ 且培训自主报名 >= 3 门 且 IDP 完成率 > 70%，但九宫格标签为"普通"或"中坚"

#### Scenario: 返回结构化数据
- **WHEN** 发现候选人
- **THEN** 每个候选人包含：员工基本信息、绩效轨迹、培训统计、IDP 完成情况、当前九宫格位置、推荐关注理由

#### Scenario: 无符合条件人员
- **WHEN** 无人满足筛选条件
- **THEN** 返回空列表并说明当前无被埋没的高潜人才

#### Scenario: 按部门过滤
- **WHEN** 传入 department_id
- **THEN** 仅分析该部门员工

### Requirement: 流失风险预警
系统 SHALL 提供 td_assess_flight_risk Tool，识别高绩效但有流失风险的员工。

#### Scenario: 识别流失风险人员
- **WHEN** 调用 td_assess_flight_risk(department_id=可选)
- **THEN** 返回高风险员工列表：绩效 A 或 B+ 且当前职级停留 >= 2 年，且无活跃 IDP 或 IDP 状态为"已放弃"

#### Scenario: 返回风险评估数据
- **WHEN** 发现风险员工
- **THEN** 每个员工包含：基本信息、绩效历史、职级停留时长、IDP 状态、加班趋势、风险信号摘要

#### Scenario: 无风险人员
- **WHEN** 无人满足条件
- **THEN** 返回空列表

### Requirement: 晋升准备度评估
系统 SHALL 提供 td_promotion_readiness Tool，评估员工的晋升准备程度。

#### Scenario: 评估单个员工
- **WHEN** 调用 td_promotion_readiness(employee_id)
- **THEN** 返回该员工的晋升评估：职级停留时间、最近绩效等级、管理类培训完成数、IDP 进度、综合就绪度指标

#### Scenario: 评估部门全员
- **WHEN** 调用 td_promotion_readiness(department_id=xxx) 不传 employee_id
- **THEN** 返回该部门所有在职员工的晋升准备度排名

#### Scenario: 就绪度指标计算
- **WHEN** 计算就绪度
- **THEN** 综合以下维度：职级停留时长(权重25%)、最近绩效(权重30%)、管理培训(权重20%)、IDP完成(权重25%)，输出 1-100 分

### Requirement: 岗位适配推荐
系统 SHALL 提供 td_find_candidates Tool，根据岗位需求推荐匹配人选。

#### Scenario: 基于技能匹配推荐
- **WHEN** 调用 td_find_candidates(requirements="需要 Python 高级、项目管理经验、数据分析能力")
- **THEN** 基于技能标签、项目经历、教育背景、绩效基线筛选匹配候选人并排名

#### Scenario: 技能数据不足时降级
- **WHEN** 系统中技能数据为空或极少
- **THEN** 返回提示"技能数据不足，建议先完善员工技能标签"，同时基于培训记录和项目经历做有限匹配

#### Scenario: 返回匹配详情
- **WHEN** 找到候选人
- **THEN** 每个候选人包含：基本信息、匹配技能、相关项目经历、绩效概况、匹配度说明

### Requirement: 完整人才画像
系统 SHALL 提供 td_talent_portrait Tool，生成员工的全维度人才画像。

#### Scenario: 生成人才画像
- **WHEN** 调用 td_talent_portrait(employee_id)
- **THEN** 汇总返回该员工所有维度数据：基本信息、教育背景、技能标签、项目经历、证书认证、绩效轨迹、培训记录、IDP、九宫格历史、岗位变动历史

#### Scenario: 部分数据缺失
- **WHEN** 某些维度（如技能、教育）无数据
- **THEN** 对应字段返回空列表，不影响其他维度的展示

### Requirement: 团队能力短板分析
系统 SHALL 提供 td_team_capability_gap Tool，分析团队的技能覆盖和能力缺口。

#### Scenario: 分析团队技能覆盖
- **WHEN** 调用 td_team_capability_gap(department_id)
- **THEN** 返回该部门所有员工的技能汇总、各技能等级分布、团队能力矩阵

#### Scenario: 技能数据不足时降级
- **WHEN** 部门员工技能数据为空或极少
- **THEN** 返回提示"技能数据不足"，同时基于培训记录推断团队能力方向

#### Scenario: 识别能力缺口
- **WHEN** 技能数据充足
- **THEN** 输出团队高频技能、稀缺技能、建议补强方向

### Requirement: 人才评估知识库
系统 SHALL 提供 talent-discovery Skill 知识库，为 LLM 分析提供评估框架。

#### Scenario: 知识库可用
- **WHEN** HR Agent 启动
- **THEN** talent-discovery skill 加载，包含人才评估维度、分析标准、报告模板等参考内容

#### Scenario: 引导分析输出
- **WHEN** Agent 使用发现 Tool 返回的数据回答用户
- **THEN** Agent 依据知识库中的评估框架，给出结构化的分析和建议

### Requirement: 权限控制
所有发现 Tool SHALL 仅限 talent_dev 角色调用。

#### Scenario: talent_dev 角色可用
- **WHEN** 当前用户 roles 包含 "talent_dev"
- **THEN** 6 个发现 Tool 全部可用

#### Scenario: 非 talent_dev 角色拒绝
- **WHEN** 当前用户无 "talent_dev" 角色
- **THEN** 调用发现 Tool 时返回权限不足错误

### Requirement: 发现结果 Schema
系统 SHALL 提供 schemas/discovery.py，定义所有发现场景的响应模型。

#### Scenario: Schema 定义完整
- **WHEN** 发现 Tool 返回数据
- **THEN** 使用对应的 Pydantic Schema 序列化，每个字段包含 Field(description="中文说明")
