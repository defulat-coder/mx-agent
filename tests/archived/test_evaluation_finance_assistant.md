# 财务助手 — Agent 评估用例

> 角色：员工（所有用户）+ 主管（`roles: ["manager"]`）+ 财务人员（`roles: ["finance"]`）
> 工具集：4 个员工工具 + 3 个主管工具 + 7 个财务人员工具，共 14 个
> Skills：3 个知识库（reimbursement-policy / budget-rules / tax-knowledge）
> 种子数据：20 报销单 + 40 明细 + 10 预算 + 15 预算使用 + 10 应付 + 5 应收

---

## 一、路由识别（Router Team → Finance Agent）

| ID | 用户输入 | 预期路由 | 验证点 |
|----|---------|---------|--------|
| RT-01 | "查看我的报销单" | Finance Assistant | 识别为财务报销查询 |
| RT-02 | "部门预算还剩多少" | Finance Assistant | 识别为财务预算查询 |
| RT-03 | "我这个月扣了多少税" | Finance Assistant | 识别为财务个税查询 |
| RT-04 | "报销标准是什么" | Finance Assistant | 识别为财务制度咨询 |
| RT-05 | "应付账款情况" | Finance Assistant | 识别为财务应付查询 |
| RT-06 | "帮我请假" | HR Assistant | 不应路由到财务 |
| RT-07 | "订会议室" | Admin Assistant | 不应路由到财务 |

---

## 二、员工自助 — 报销查询（2 个工具）

### 2.1 我的报销单 `fin_get_my_reimbursements`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-01 | "查看我的报销单" | fin_get_my_reimbursements | 无 | 返回当前用户的报销单列表 |
| EQ-02 | "我有哪些待审批的报销" | fin_get_my_reimbursements | status="pending" | 仅返回 pending 状态 |
| EQ-03 | "已通过的报销单" | fin_get_my_reimbursements | status="approved" | 仅返回 approved 状态 |

### 2.2 报销单详情 `fin_get_reimbursement_detail`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-04 | "查看报销单 3 的详情" | fin_get_reimbursement_detail | reimbursement_id=3 | 返回含明细行的完整信息 |
| EQ-05 | "看看别人的报销单 1" | fin_get_reimbursement_detail | reimbursement_id=1 | 非本人报销单返回权限不足 |

---

## 三、员工自助 — 预算与个税（2 个工具）

### 3.1 部门预算 `fin_get_department_budget`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| EQ-06 | "部门预算还有多少" | fin_get_department_budget | 返回部门当年预算余额 |
| EQ-07 | "去年的部门预算" | fin_get_department_budget | year 参数正确传递 |

### 3.2 个税查询 `fin_get_my_tax`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-08 | "我这个月扣了多少税" | fin_get_my_tax | 无（默认近 3 月） | 跨域读 HR SalaryRecord |
| EQ-09 | "查看 2026-01 的个税" | fin_get_my_tax | year_month="2026-01" | 指定月份查询 |

---

## 四、Skills 知识库咨询（3 个 Skills）

### 4.1 报销政策 `reimbursement-policy`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-01 | "差旅报销标准是多少" | 使用 reimbursement-policy Skill | 包含差旅费标准 |
| SK-02 | "报销审批流程是什么" | 使用 reimbursement-policy Skill | 包含主管→财务审核流程 |
| SK-03 | "发票有什么要求" | 使用 reimbursement-policy Skill | 包含发票抬头/识别号/时效要求 |
| SK-04 | "报销有时间限制吗" | 使用 reimbursement-policy Skill | 包含 30 天时限 |

### 4.2 预算制度 `budget-rules`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-05 | "预算超支怎么办" | 使用 budget-rules Skill | 包含超支审批流程 |
| SK-06 | "预算调整需要走什么流程" | 使用 budget-rules Skill | 包含预算调整审批规定 |

### 4.3 个税知识 `tax-knowledge`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-07 | "个税怎么算的" | 使用 tax-knowledge Skill | 包含个税税率表或计算方式 |
| SK-08 | "专项扣除有哪些" | 使用 tax-knowledge Skill | 包含子女教育/住房贷款等 |

---

## 五、主管权限（3 个工具）

### 5.1 预算总览 `fin_mgr_get_budget_overview`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| MQ-01 | "我们部门预算执行情况" | fin_mgr_get_budget_overview | 返回总额/已用/余额/执行率 |

### 5.2 费用明细 `fin_mgr_get_expense_detail`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MQ-02 | "部门本月费用明细" | fin_mgr_get_expense_detail | year_month | 返回费用明细列表 |
| MQ-03 | "部门差旅费用" | fin_mgr_get_expense_detail | category="差旅" | 按科目筛选 |

### 5.3 预算预警 `fin_mgr_get_budget_alert`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| MQ-04 | "预算有超支风险吗" | fin_mgr_get_budget_alert | 返回执行率≥80%的预算项 |

---

## 六、财务人员 — 报销管理（3 个工具）

### 6.1 全部报销查询 `fin_admin_get_all_reimbursements`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-01 | "查看所有待审批的报销单" | fin_admin_get_all_reimbursements | status="pending" | 仅返回 pending |
| AQ-02 | "技术部的差旅报销" | fin_admin_get_all_reimbursements | department_id, type="差旅" | 多条件筛选 |

### 6.2 报销审核 `fin_admin_review_reimbursement`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-01 | "通过报销单 5" | fin_admin_review_reimbursement | id=5, action="approve" | 状态→approved，自动扣预算 |
| AA-02 | "退回报销单 8，发票不合规" | fin_admin_review_reimbursement | id=8, action="return", remark | 状态→returned |
| AA-03 | "拒绝报销单 10" | fin_admin_review_reimbursement | id=10, action="reject" | 状态→rejected |

### 6.3 费用汇总 `fin_admin_get_expense_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-03 | "各部门费用汇总" | fin_admin_get_expense_summary | group_by="department" | 按部门分组 |
| AQ-04 | "本月各科目费用" | fin_admin_get_expense_summary | group_by="type" | 按类型分组 |

---

## 七、财务人员 — 预算与应收应付（4 个工具）

### 7.1 预算分析 `fin_admin_get_budget_analysis`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-05 | "全公司预算执行分析" | fin_admin_get_budget_analysis | 返回各部门预算执行率 |

### 7.2 应付账款 `fin_admin_get_payables`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-06 | "查看待付款项" | fin_admin_get_payables | status="pending" | 返回待付列表 |
| AQ-07 | "有逾期的应付款吗" | fin_admin_get_payables | status="overdue" | 返回逾期列表 |

### 7.3 应收账款 `fin_admin_get_receivables`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-08 | "应收账款情况" | fin_admin_get_receivables | 返回全部应收款 |

### 7.4 开票处理 `fin_admin_process_invoice_request`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-04 | "帮客户A公司开一张 5 万元的发票" | fin_admin_process_invoice_request | customer, amount=50000 | 返回开票结果 |

---

## 八、权限校验

| ID | 场景 | 用户输入 | 测试用户 | 期望结果 |
|----|------|---------|---------|---------|
| PR-01 | 员工调主管工具 | "部门预算执行率" | 普通员工 | 返回权限不足 |
| PR-02 | 员工调财务工具 | "审核报销单 1" | 普通员工 | 返回权限不足 |
| PR-03 | 主管调财务工具 | "全公司报销汇总" | 仅 manager 角色 | 返回权限不足 |

---

## 九、边界与异常场景

| ID | 场景 | 用户输入 | 期望行为 |
|----|------|---------|---------|
| EX-01 | 超出范围 | "帮我订会议室" | 告知不在财务范围，建议联系行政 |
| EX-02 | 模糊意图 | "帮我查一下钱" | 追问是查报销/预算/个税 |
| EX-03 | Skills → 工具 | "报销标准是什么？那帮我查报销进度" | 先查 Skill 回答制度，再调工具 |
| EX-04 | 审核不存在的单 | "通过报销单 9999" | 返回报销单不存在 |
| EX-05 | 重复审核 | "再次通过已审核的报销单" | 返回状态不允许审核 |

---

## 十、评估统计

| 维度 | 数量 |
|------|------|
| 路由识别 | 7 |
| 员工报销 | 5 |
| 员工预算/个税 | 4 |
| Skills 咨询 | 8 |
| 主管权限 | 4 |
| 财务报销管理 | 7 |
| 财务预算/应收应付 | 6 |
| 权限校验 | 3 |
| 边界异常 | 5 |
| **合计** | **49** |
