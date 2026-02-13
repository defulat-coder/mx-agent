# 主管角色 — Agent 评估用例

> 角色标识：`roles: ["manager"]`，需有 department_id
> 工具集：继承普通员工 10 个 + 团队查询 6 个 + 审批 2 个，共 18 个

---

## 一、团队查询（6 个工具）

### 1.1 团队成员 `get_team_members`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-01 | "我的团队有哪些人" | get_team_members | 自动取 dept_id | 返回管辖范围内全部员工 |
| MGR-02 | "我手下几个人" | get_team_members | 同上 | Agent 统计人数 |

### 1.2 团队考勤 `get_team_attendance`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-03 | "团队这个月考勤情况" | get_team_attendance | 无过滤 | 返回全员当月考勤 |
| MGR-04 | "张三上周考勤" | get_team_attendance | employee_id=1, start/end=上周 | 单人+日期过滤 |
| MGR-05 | "团队有没有考勤异常" | get_team_attendance | status="异常" | 过滤异常记录 |
| MGR-06 | "看看 1 月团队迟到记录" | get_team_attendance | status="异常" 或 "迟到", start/end=1月 | 日期+状态过滤 |

### 1.3 团队请假记录 `get_team_leave_requests`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-07 | "有没有待审批的请假" | get_team_leave_requests | status="待审批" | 仅返回待审批 |
| MGR-08 | "团队今年请假记录" | get_team_leave_requests | status=None | 返回当年全部 |

### 1.4 团队假期余额 `get_team_leave_balances`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-09 | "团队假期余额" | get_team_leave_balances | employee_id=None | 全员假期余额 |
| MGR-10 | "张三还有多少年假" | get_team_leave_balances | employee_id=1 | 单人余额 |

### 1.5 团队加班记录 `get_team_overtime_records`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-11 | "团队这个月加班情况" | get_team_overtime_records | year_month=None | 当月全员加班 |
| MGR-12 | "有没有待审批的加班" | get_team_overtime_records | status="待审批" | 过滤待审批 |
| MGR-13 | "2025年1月团队加班记录" | get_team_overtime_records | year_month="2025-01" | 指定月份 |

### 1.6 员工档案 `get_employee_profile`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-14 | "看一下张三的档案" | get_employee_profile | employee_id=1 | 含基本信息+绩效+履历，不含薪资社保 |
| MGR-15 | "李四的绩效记录" | get_employee_profile | employee_id=2 | 从档案中提取绩效部分 |
| MGR-16 | "查一下非下属（其他部门）的档案" | get_employee_profile | employee_id=非管辖员工 | 返回权限不足提示 |

---

## 二、审批操作（2 个工具）

### 2.1 请假审批 `approve_leave_request`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-17 | "通过张三的请假申请，申请编号 5" | approve_leave_request | request_id=5, action="通过" | 返回审批成功 |
| MGR-18 | "拒绝编号 3 的请假，理由是人手不足" | approve_leave_request | request_id=3, action="拒绝", comment="人手不足" | 含拒绝备注 |
| MGR-19 | "审批请假" | — | — | Agent 先查待审批列表再确认 |

### 2.2 加班审批 `approve_overtime_request`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| MGR-20 | "通过加班申请 8" | approve_overtime_request | record_id=8, action="通过" | 返回审批成功 |
| MGR-21 | "拒绝加班记录 10" | approve_overtime_request | record_id=10, action="拒绝" | 返回审批结果 |

---

## 三、角色混合（主管 + 普通员工）

验证主管仍可使用普通员工工具查询自己的数据。

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| MIX-01 | "我的工资" | get_salary_records | 查自己薪资，非团队 |
| MIX-02 | "我还有多少年假" | get_leave_balance | 查自己余额，非团队 |
| MIX-03 | "帮我请年假下周一" | apply_leave | 主管自己请假 |
| MIX-04 | "我的考勤" vs "团队考勤" | get_attendance vs get_team_attendance | 正确区分自己与团队 |

---

## 四、权限边界测试

| ID | 场景 | 用户输入 | 预期行为 |
|----|------|---------|---------|
| PERM-01 | 查下属薪资 | "张三的工资多少" | Agent 告知主管无权查看下属薪资 |
| PERM-02 | 查下属社保 | "李四的社保缴纳" | Agent 告知主管无权查看下属社保 |
| PERM-03 | 查非下属档案 | "查一下其他部门王五的档案" | get_employee_profile 返回权限不足 |
| PERM-04 | 使用 admin 工具 | "全公司人员统计" | Agent 告知需管理者权限 |
| PERM-05 | 使用 td_ 工具 | "谁有流失风险" | Agent 告知需人才发展权限 |
| PERM-06 | 审批非下属请假 | "通过其他部门的请假" | approve_leave_request 返回权限不足 |

---

## 五、工具选择歧义测试

| ID | 用户输入 | 期望工具 | 不应调用 | 说明 |
|----|---------|---------|---------|------|
| AMB-01 | "请假记录" | get_leave_requests（自己） | get_team_leave_requests | 未指定团队则查自己 |
| AMB-02 | "团队请假记录" | get_team_leave_requests | get_leave_requests | 明确说团队 |
| AMB-03 | "我的考勤" | get_attendance | get_team_attendance | "我的"指自己 |
| AMB-04 | "大家的假期余额" | get_team_leave_balances | get_leave_balance | "大家"指团队 |
| AMB-05 | "张三的档案" | get_employee_profile | admin_get_employee_profile | 主管用主管工具 |

---

## 六、审批流程测试

| ID | 场景 | 对话流程 | 验证点 |
|----|------|---------|--------|
| FLOW-01 | 先查后批（请假） | "有什么待审批的" → 列出 → "通过第一个" | 先 get_team_leave_requests(status="待审批") 再 approve |
| FLOW-02 | 先查后批（加班） | "待审批的加班" → 列出 → "全部通过" | 先查后逐个审批 |
| FLOW-03 | 审批确认 | "审批张三请假" → Agent 应先确认具体哪个申请 | 不盲目审批 |

---

## 七、边界与异常

| ID | 场景 | 用户输入 | 预期行为 |
|----|------|---------|---------|
| EDGE-01 | 空团队 | 新部门无下属 | get_team_members 返回空列表 |
| EDGE-02 | 不存在的申请 ID | "通过请假申请 999" | 返回申请不存在提示 |
| EDGE-03 | 审批已处理的申请 | "通过已经批过的申请 1" | 返回已处理提示 |
| EDGE-04 | action 参数错误 | "把请假 5 标记为取消" | Agent 告知只支持通过/拒绝 |
