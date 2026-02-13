## ADDED Requirements

### Requirement: 模拟企业制度文档
系统 SHALL 提供 5 份模拟企业制度 Markdown 文档，放置在 `data/knowledge/docs/` 目录。

#### Scenario: 员工手册
- **WHEN** 查看 `data/knowledge/docs/员工手册.md`
- **THEN** 包含公司简介、组织架构、行为规范、奖惩制度、员工福利等章节，约 200-300 行

#### Scenario: 财务管理制度
- **WHEN** 查看 `data/knowledge/docs/财务管理制度.md`
- **THEN** 包含预算管理、费用报销细则、资产管理、审计监督等章节，约 150-200 行

#### Scenario: IT管理规范
- **WHEN** 查看 `data/knowledge/docs/IT管理规范.md`
- **THEN** 包含信息安全、设备管理、网络使用、数据备份、应急响应等章节，约 150-200 行

#### Scenario: 行政管理制度
- **WHEN** 查看 `data/knowledge/docs/行政管理制度.md`
- **THEN** 包含办公环境管理、会议管理、车辆管理、档案管理等章节，约 150-200 行

#### Scenario: 法务合规手册
- **WHEN** 查看 `data/knowledge/docs/法务合规手册.md`
- **THEN** 包含合同管理流程、知识产权保护、反腐败政策、数据隐私、争议解决等章节，约 150-200 行

### Requirement: 文档内容与现有 Skills 互补
模拟文档 SHALL 包含比现有 Skills 更详细、更广泛的内容，形成互补关系。

#### Scenario: 内容差异化
- **WHEN** Skills 已覆盖核心规则（如年假计算公式、报销标准）
- **THEN** 模拟文档侧重覆盖 Skills 未涉及的内容（如公司文化、组织架构、奖惩细则、车辆管理等）
