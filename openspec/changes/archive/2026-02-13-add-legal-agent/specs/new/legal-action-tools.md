# legal-action-tools

法务人员操作工具

## ADDED Requirements

### Requirement: leg_admin_review_contract

法务人员审查合同：approved/returned。需 legal 角色。

参数：contract_id, action(approved/returned), opinion。

审查通过 → Contract.status 改 approved；退回 → Contract.status 改 returned。同时创建 ContractReview 记录。

#### Scenario: 审查通过
- **WHEN** 法务人员调用 leg_admin_review_contract，action=approved
- **THEN** Contract.status 变为 approved，创建 ContractReview 记录

#### Scenario: 退回修改
- **WHEN** 法务人员调用 leg_admin_review_contract，action=returned
- **THEN** Contract.status 变为 returned，创建含退回意见的 ContractReview 记录

#### Scenario: 非 pending 状态合同
- **WHEN** 合同 status 不是 pending
- **THEN** 返回错误提示"该合同当前状态不可审查"

### Requirement: leg_admin_analyze_contract

法务人员对合同进行 LLM 辅助条款分析。需 legal 角色。

参数：contract_id。

实现：读取 Contract 的 content + key_terms，组装 prompt 调用 get_model()，返回结构化分析结果（条款摘要 + 风险点 + 建议）。结果附 disclaimer。

#### Scenario: 条款分析
- **WHEN** 法务人员调用 leg_admin_analyze_contract 传有效 contract_id
- **THEN** 调用 LLM 分析合同内容，返回 ContractAnalysisResult（summary, risks, suggestions）+ disclaimer

#### Scenario: 合同无内容
- **WHEN** Contract.content 为空
- **THEN** 返回错误提示"该合同暂无内容可分析"
