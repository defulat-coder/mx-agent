# legal-data-models

法务数据模型 — 3 张 SQLAlchemy ORM 表 + Pydantic Schema

## ADDED Requirements

### Requirement: ContractTemplate 模型

文件 `app/models/legal/contract_template.py`，表名 `contract_templates`。

字段：name, type(劳动合同/保密协议/采购合同/销售合同/服务合同/其他), description, file_url。

#### Scenario: 模型定义
- **WHEN** 定义 ContractTemplate 模型
- **THEN** 继承 Base，包含 id/created_at/updated_at + name(String64) + type(String32) + description(Text) + file_url(String256)，所有 mapped_column 含 comment

### Requirement: Contract 模型

文件 `app/models/legal/contract.py`，表名 `contracts`。

字段：contract_no(唯一), title, type, party_a, party_b, amount(Numeric), start_date, end_date, status(draft/pending/approved/rejected/returned/expired/terminated), content(Text,合同摘要), key_terms(Text,JSON格式关键条款), submitted_by(FK employees.id), department_id(FK departments.id)。

#### Scenario: 模型定义
- **WHEN** 定义 Contract 模型
- **THEN** 继承 Base，contract_no 唯一索引，status 默认 draft，amount 为 Numeric(12,2)，content 和 key_terms 为 Text 类型

### Requirement: ContractReview 模型

文件 `app/models/legal/contract_review.py`，表名 `contract_reviews`。

字段：contract_id(FK contracts.id), reviewer_id(FK employees.id), action(approved/returned), opinion(Text)。

#### Scenario: 模型定义
- **WHEN** 定义 ContractReview 模型
- **THEN** 继承 Base，contract_id 和 reviewer_id 为外键，action 为 String16

### Requirement: __init__.py 导出

`app/models/legal/__init__.py` SHALL 导入并导出全部 3 个模型。

#### Scenario: 模块导入
- **WHEN** 执行 `from app.models.legal import ContractTemplate, Contract, ContractReview`
- **THEN** 成功导入全部模型

### Requirement: Pydantic Schema

`app/schemas/legal.py` SHALL 定义全部响应模型，所有字段带 `Field(description="中文说明")`。

包含：ContractTemplateResponse, ContractResponse, ContractReviewResponse, ContractAnalysisResult, ContractStatsResponse。

#### Scenario: Schema 定义
- **WHEN** 需要序列化法务数据
- **THEN** 使用对应 Response Schema，ContractAnalysisResult 包含 summary/risks/suggestions 字段
