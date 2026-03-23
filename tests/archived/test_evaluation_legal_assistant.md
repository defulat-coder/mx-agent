# 法务助手 — Agent 评估用例

> 角色：员工（所有用户）+ 法务人员（`roles: ["legal"]`）
> 工具集：3 个员工工具 + 5 个法务人员工具，共 8 个
> Skills：3 个知识库（labor-law / contract-knowledge / compliance）
> 种子数据：10 模板 + 60 合同 + 30 审查记录

---

## 一、路由识别（Router Team → Legal Agent）

| ID | 用户输入 | 预期路由 | 验证点 |
|----|---------|---------|--------|
| RT-01 | "有劳动合同模板吗" | Legal Assistant | 识别为法务合同模板查询 |
| RT-02 | "我的合同审批到哪了" | Legal Assistant | 识别为法务合同进度查询 |
| RT-03 | "竞业限制是什么意思" | Legal Assistant | 识别为法务法律咨询 |
| RT-04 | "收到可疑邮件怎么办" | Legal Assistant 或 IT Assistant | 可能涉及合规或 IT 安全 |
| RT-05 | "公司保密协议规定是什么" | Legal Assistant | 识别为法务合同知识 |
| RT-06 | "帮我请假" | HR Assistant | 不应路由到法务 |
| RT-07 | "报销标准是什么" | Finance Assistant | 不应路由到法务 |

---

## 二、员工自助 — 合同模板（2 个工具）

### 2.1 查询模板 `leg_get_templates`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-01 | "有哪些合同模板" | leg_get_templates | 无 | 返回全部模板列表 |
| EQ-02 | "劳动合同模板" | leg_get_templates | type="劳动合同" | 仅返回劳动合同类型 |
| EQ-03 | "有保密协议模板吗" | leg_get_templates | type="保密协议" | 返回保密协议模板 |
| EQ-04 | "采购合同模板有几个" | leg_get_templates | type="采购合同" | 返回采购合同模板 |

### 2.2 下载模板 `leg_get_template_download`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-05 | "下载标准劳动合同模板" | leg_get_template_download | template_id=1 | 返回模板信息 + file_url |
| EQ-06 | "下载不存在的模板" | leg_get_template_download | template_id=999 | 返回模板不存在 |

---

## 三、员工自助 — 合同进度（1 个工具）

### 3.1 我的合同 `leg_get_my_contracts`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-07 | "我提交的合同审批到哪了" | leg_get_my_contracts | 无 | 返回 submitted_by=当前用户的合同列表 |
| EQ-08 | "我有哪些待审查的合同" | leg_get_my_contracts | status="pending" | 仅返回 pending 状态 |
| EQ-09 | "已通过的合同" | leg_get_my_contracts | status="approved" | 仅返回 approved 状态 |

---

## 四、Skills 知识库咨询（3 个 Skills）

### 4.1 劳动法 `labor-law`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-01 | "试用期最长多久" | 使用 labor-law Skill | 包含按合同期限划分的试用期时长 |
| SK-02 | "被辞退有补偿吗" | 使用 labor-law Skill | 包含经济补偿计算标准（N+1） |
| SK-03 | "竞业限制期限是多久" | 使用 labor-law Skill | 包含不超过 2 年的规定 |
| SK-04 | "怀孕了能被辞退吗" | 使用 labor-law Skill | 包含孕期/产期/哺乳期解雇保护 |

### 4.2 合同知识 `contract-knowledge`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-05 | "合同签订流程是什么" | 使用 contract-knowledge Skill | 包含起草→审核→法务→审批→用印 |
| SK-06 | "多少金额的合同需要总经理审批" | 使用 contract-knowledge Skill | 包含分级审批权限表 |
| SK-07 | "保密协议保密期是多久" | 使用 contract-knowledge Skill | 包含离职后 2 年 |
| SK-08 | "职务发明归谁" | 使用 contract-knowledge Skill | 包含知识产权归公司 |

### 4.3 合规知识 `compliance`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-09 | "可以收客户礼品吗" | 使用 compliance Skill | 包含 200 元限额规定 |
| SK-10 | "数据泄露怎么处理" | 使用 compliance Skill | 包含报告→评估→补救→72h报监管 |
| SK-11 | "合规举报渠道" | 使用 compliance Skill | 包含邮箱/热线/匿名系统 |

---

## 五、法务人员 — 合同管理（3 个查询工具）

### 5.1 合同台账 `leg_admin_get_contracts`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-01 | "查看全部合同" | leg_admin_get_contracts | 无 | 返回全公司合同列表 |
| AQ-02 | "待审查的采购合同" | leg_admin_get_contracts | status="pending", type="采购合同" | 多条件筛选 |
| AQ-03 | "技术部的合同" | leg_admin_get_contracts | department_id | 按部门筛选 |

### 5.2 到期预警 `leg_admin_get_expiring`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-04 | "有哪些合同快到期了" | leg_admin_get_expiring | days=30 | 返回 30 天内到期的 approved 合同 |
| AQ-05 | "60 天内到期的合同" | leg_admin_get_expiring | days=60 | days 参数正确传递 |

### 5.3 统计报表 `leg_admin_get_stats`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-06 | "合同统计报表" | leg_admin_get_stats | 返回总数/金额/状态分布/类型分布/到期数 |

---

## 六、法务人员 — 合同审查与分析（2 个操作工具）

### 6.1 合同审查 `leg_admin_review_contract`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-01 | "审查通过合同 5" | leg_admin_review_contract | contract_id=5, action="approved" | 状态→approved，创建审查记录 |
| AA-02 | "退回合同 8，缺少违约条款" | leg_admin_review_contract | id=8, action="returned", opinion | 状态→returned |
| AA-03 | "审查已通过的合同 1" | leg_admin_review_contract | 非 pending 合同 | 返回"当前状态不可审查" |
| AA-04 | "审查合同 9999" | leg_admin_review_contract | contract_id=9999 | 返回合同不存在 |

### 6.2 条款分析 `leg_admin_analyze_contract`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-05 | "分析合同 3 的条款" | leg_admin_analyze_contract | contract_id=3 | 返回 summary/risks/suggestions + disclaimer |
| AA-06 | "帮我分析一下合同 10 有什么风险" | leg_admin_analyze_contract | contract_id=10 | LLM 返回风险点列表 |
| AA-07 | "分析无内容的合同" | leg_admin_analyze_contract | content 为空的合同 | 返回"暂无内容可分析" |

---

## 七、权限校验

| ID | 场景 | 用户输入 | 测试用户 | 期望结果 |
|----|------|---------|---------|---------|
| PR-01 | 员工调法务工具 | "查看全部合同" | 普通员工 | 返回权限不足 |
| PR-02 | 员工调法务工具 | "分析合同 1 的条款" | 普通员工 | 返回权限不足 |
| PR-03 | 员工调法务工具 | "审查通过合同 5" | 普通员工 | 返回权限不足 |

---

## 八、边界与异常场景

| ID | 场景 | 用户输入 | 期望行为 |
|----|------|---------|---------|
| EX-01 | 超出范围 | "帮我查工资" | 告知不在法务范围，建议联系 HR |
| EX-02 | 模糊意图 | "我有个合同问题" | 追问是查模板/查进度/法律咨询 |
| EX-03 | Skills → 工具 | "合同审批流程是什么？那帮我查我的合同进度" | 先查 Skill 回答流程，再调 leg_get_my_contracts |
| EX-04 | 条款分析免责 | 任何条款分析结果 | 必须附带 disclaimer "仅供参考，不构成法律意见" |
| EX-05 | 多轮对话 | 先"有什么模板"→选择"下载保密协议"→"帮我查合同进度" | 连续多个工具调用 |

---

## 九、评估统计

| 维度 | 数量 |
|------|------|
| 路由识别 | 7 |
| 员工模板查询 | 6 |
| 员工合同进度 | 3 |
| Skills 咨询 | 11 |
| 法务合同管理 | 6 |
| 法务审查与分析 | 7 |
| 权限校验 | 3 |
| 边界异常 | 5 |
| **合计** | **48** |
