## ADDED Requirements

### Requirement: 技能标签模型
系统 SHALL 提供 Skill ORM 模型，存储员工的技能标签信息。

#### Scenario: 模型字段完整
- **WHEN** 创建 Skill 记录
- **THEN** 包含字段：employee_id（FK→employees）、name（技能名称）、category（技术/管理/业务/通用）、level（初级/中级/高级/专家）、source（自评/上级评/认证）、verified（是否已确认）

#### Scenario: 同一员工多技能
- **WHEN** 为同一员工录入多个技能
- **THEN** 每个技能独立一条记录，employee_id 相同

#### Scenario: 对应 Schema 可用
- **WHEN** 查询返回 Skill 数据
- **THEN** 通过 SkillResponse Schema 返回所有字段，每个字段包含 description

### Requirement: 教育背景模型
系统 SHALL 提供 Education ORM 模型，存储员工的教育背景信息。

#### Scenario: 模型字段完整
- **WHEN** 创建 Education 记录
- **THEN** 包含字段：employee_id（FK→employees）、degree（大专/本科/硕士/博士/MBA）、major（专业）、school（院校名称）、graduation_year（毕业年份）

#### Scenario: 对应 Schema 可用
- **WHEN** 查询返回 Education 数据
- **THEN** 通过 EducationResponse Schema 返回所有字段

### Requirement: 项目经历模型
系统 SHALL 提供 ProjectExperience ORM 模型，存储员工的项目参与记录。

#### Scenario: 模型字段完整
- **WHEN** 创建 ProjectExperience 记录
- **THEN** 包含字段：employee_id（FK→employees）、project_name（项目名称）、role（负责人/核心成员/参与者）、start_date（开始日期）、end_date（结束日期，可空表示进行中）、description（项目描述）、achievement（关键成果）

#### Scenario: 对应 Schema 可用
- **WHEN** 查询返回 ProjectExperience 数据
- **THEN** 通过 ProjectExperienceResponse Schema 返回所有字段

### Requirement: 证书认证模型
系统 SHALL 提供 Certificate ORM 模型，存储员工的证书认证信息。

#### Scenario: 模型字段完整
- **WHEN** 创建 Certificate 记录
- **THEN** 包含字段：employee_id（FK→employees）、name（证书名称）、issuer（颁发机构）、issue_date（颁发日期）、expiry_date（有效期，可空表示永久有效）、category（专业技术/管理/语言/行业）

#### Scenario: 对应 Schema 可用
- **WHEN** 查询返回 Certificate 数据
- **THEN** 通过 CertificateResponse Schema 返回所有字段

### Requirement: 基础 CRUD 服务
系统 SHALL 在 services/hr.py 中为 4 个新模型提供查询函数。

#### Scenario: 查询员工技能列表
- **WHEN** 调用 get_employee_skills(employee_id)
- **THEN** 返回该员工所有技能标签，支持按 category 过滤

#### Scenario: 查询员工教育背景
- **WHEN** 调用 get_employee_education(employee_id)
- **THEN** 返回该员工所有教育记录

#### Scenario: 查询员工项目经历
- **WHEN** 调用 get_employee_projects(employee_id)
- **THEN** 返回该员工所有项目经历，支持按 role 过滤

#### Scenario: 查询员工证书
- **WHEN** 调用 get_employee_certificates(employee_id)
- **THEN** 返回该员工所有证书，支持按 category 过滤

### Requirement: 数据库自动建表
系统 SHALL 在启动时自动创建 4 张新表（skills / educations / project_experiences / certificates）。

#### Scenario: 首次启动建表
- **WHEN** 应用启动且表不存在
- **THEN** 自动创建表结构，无需手动迁移
