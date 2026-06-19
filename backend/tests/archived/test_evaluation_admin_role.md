# 管理者角色 — Agent 评估用例

> 角色标识：`roles: ["admin"]`
> 工具集：继承普通员工 10 个 + 全公司查询 11 个 + 全公司审批 2 个，共 23 个

---

## 一、全公司数据查询（7 个工具）

### 1.1 全公司员工列表 `admin_get_all_employees`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-01 | "公司现在一共多少人" | admin_get_all_employees | 无 | Agent 统计返回列表长度 |
| ADM-02 | "列出全公司员工" | admin_get_all_employees | 无 | 返回所有部门员工 |

### 1.2 任意员工薪资 `admin_get_employee_salary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-03 | "张三这个月工资多少" | admin_get_employee_salary | employee_id=1, year_month=当月 | 返回薪资明细 |
| ADM-04 | "李四 2025 年 1 月薪资" | admin_get_employee_salary | employee_id=2, year_month="2025-01" | 指定月份 |

### 1.3 任意员工社保 `admin_get_employee_social_insurance`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-05 | "张三的社保缴纳情况" | admin_get_employee_social_insurance | employee_id=1 | 返回社保明细 |

### 1.4 任意员工完整档案 `admin_get_employee_profile`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-06 | "查一下张三的完整档案" | admin_get_employee_profile | employee_id=1 | 含基本信息+绩效+履历+薪资+社保 |
| ADM-07 | "看看工号 19 的员工信息" | admin_get_employee_profile | employee_id=19 | 含全部维度 |

### 1.5 全公司请假记录 `admin_get_all_leave_requests`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-08 | "全公司待审批的请假" | admin_get_all_leave_requests | status="待审批" | 过滤待审批 |
| ADM-09 | "全公司请假记录" | admin_get_all_leave_requests | status=None | 返回全部 |

### 1.6 全公司考勤 `admin_get_all_attendance`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-10 | "全公司这周考勤异常" | admin_get_all_attendance | status="异常", start/end=本周 | 状态+日期过滤 |
| ADM-11 | "全公司 1 月考勤记录" | admin_get_all_attendance | start_date="2025-01-01", end_date="2025-01-31" | 日期过滤 |

### 1.7 全公司加班 `admin_get_all_overtime_records`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-12 | "全公司待审批的加班" | admin_get_all_overtime_records | status="待审批" | 过滤待审批 |
| ADM-13 | "2025 年 1 月全公司加班记录" | admin_get_all_overtime_records | year_month="2025-01" | 指定月份 |

---

## 二、汇总报表（4 个工具）

### 2.1 部门人员统计 `admin_get_department_headcount`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-14 | "各部门人数分布" | admin_get_department_headcount | 无 | 含在职+试用期人数 |
| ADM-15 | "公司人员编制" | admin_get_department_headcount | 无 | 同上 |

### 2.2 考勤汇总 `admin_get_attendance_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-16 | "本月考勤汇总" | admin_get_attendance_summary | start/end=本月 | 正常/迟到/早退/缺卡人次 |
| ADM-17 | "1 月考勤统计" | admin_get_attendance_summary | start_date="2025-01-01", end_date="2025-01-31" | 指定月份 |

### 2.3 薪资汇总 `admin_get_salary_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-18 | "各部门薪资总额" | admin_get_salary_summary | year_month=None | 员工数+总额+平均 |
| ADM-19 | "2025 年 1 月薪资汇总" | admin_get_salary_summary | year_month="2025-01" | 指定月份 |

### 2.4 假期汇总 `admin_get_leave_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-20 | "假期使用情况统计" | admin_get_leave_summary | 无 | 各类型已用天数+待审批数 |
| ADM-21 | "待审批请假有多少" | admin_get_leave_summary | 无 | 从汇总中提取待审批数 |

---

## 三、全公司审批（2 个工具）

### 3.1 请假审批 `admin_approve_leave_request`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-22 | "通过请假申请 12" | admin_approve_leave_request | request_id=12, action="通过" | 不受部门限制 |
| ADM-23 | "拒绝请假 15，理由项目紧急" | admin_approve_leave_request | request_id=15, action="拒绝", comment="项目紧急" | 含备注 |

### 3.2 加班审批 `admin_approve_overtime_request`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| ADM-24 | "通过加班记录 20" | admin_approve_overtime_request | record_id=20, action="通过" | 全公司范围 |
| ADM-25 | "拒绝加班申请 22" | admin_approve_overtime_request | record_id=22, action="拒绝" | 返回审批结果 |

---

## 四、角色混合（admin + 普通员工）

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| MIX-01 | "我的工资" | get_salary_records | 查自己薪资用员工工具 |
| MIX-02 | "张三的工资" | admin_get_employee_salary | 查他人薪资用 admin 工具 |
| MIX-03 | "我要请假" | apply_leave | admin 自己也能办理业务 |
| MIX-04 | "我的考勤" vs "全公司考勤" | get_attendance vs admin_get_all_attendance | 正确区分自己与全公司 |

---

## 五、权限边界测试

| ID | 场景 | 用户输入 | 预期行为 |
|----|------|---------|---------|
| PERM-01 | admin 不等于 talent_dev | "谁有流失风险" | Agent 告知需人才发展权限 |
| PERM-02 | admin 不等于 talent_dev | "九宫格分布" | Agent 告知需人才发展权限 |
| PERM-03 | admin 使用主管团队工具 | "我的团队成员" | 若无 manager 角色则告知无权限 |

---

## 六、工具选择歧义测试

| ID | 用户输入 | 期望工具 | 不应调用 | 说明 |
|----|---------|---------|---------|------|
| AMB-01 | "张三的档案" | admin_get_employee_profile | get_employee_profile | admin 用 admin 工具 |
| AMB-02 | "全公司有多少人" | admin_get_department_headcount 或 admin_get_all_employees | get_team_members | 全公司级别 |
| AMB-03 | "各部门薪资对比" | admin_get_salary_summary | admin_get_employee_salary | 汇总报表非个人查询 |
| AMB-04 | "考勤异常统计" | admin_get_attendance_summary | admin_get_all_attendance | 汇总 vs 明细 |
| AMB-05 | "我的社保" | get_social_insurance | admin_get_employee_social_insurance | "我的"用员工工具 |

---

## 七、多工具组合测试

| ID | 用户输入 | 期望工具组合 | 验证点 |
|----|---------|------------|--------|
| COMBO-01 | "各部门人数和薪资对比" | admin_get_department_headcount + admin_get_salary_summary | 两个报表组合 |
| COMBO-02 | "全公司待审批的请假和加班" | admin_get_all_leave_requests + admin_get_all_overtime_records | 两者均 status="待审批" |
| COMBO-03 | "张三的档案和最近考勤" | admin_get_employee_profile + admin_get_all_attendance(employee 维度) | 档案+考勤 |

---

## 八、边界与异常

| ID | 场景 | 用户输入 | 预期行为 |
|----|------|---------|---------|
| EDGE-01 | 不存在的员工 | "查一下员工 999 的档案" | 返回空或不存在提示 |
| EDGE-02 | 不存在的申请 | "通过请假 999" | 返回申请不存在 |
| EDGE-03 | 薪资未出月份 | "下个月全公司薪资" | 返回空数据 |
| EDGE-04 | 审批已处理申请 | "再次通过请假 1" | 返回已处理提示 |
