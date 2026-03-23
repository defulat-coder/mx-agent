# 人才发展角色 — Agent 评估用例

> 角色标识：`roles: ["talent_dev"]`，种子用户：孙八（id=6）
> 工具集：17 个 `td_` 查询工具 + 6 个 `td_` 发现工具，共 23 个

---

## 一、个人数据查询（7 个工具）

### 1.1 完整档案 `td_get_employee_profile`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-01 | "帮我查一下张三的档案" | td_get_employee_profile | employee_id=1 | 返回含基本信息+绩效+履历+薪资+社保 |
| TD-02 | "看看工号 15 的员工资料" | td_get_employee_profile | employee_id=15 | 正确识别工号→employee_id |
| TD-03 | "查一个不存在的员工 999" | td_get_employee_profile | employee_id=999 | 无异常，返回空或错误提示 |

### 1.2 培训记录 `td_get_employee_training`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-04 | "张三参加过哪些培训" | td_get_employee_training | employee_id=1 | 返回培训列表 |
| TD-05 | "李四已完成的培训有哪些" | td_get_employee_training | employee_id=2, status="已完成" | status 过滤生效 |
| TD-06 | "看看王五还在进行中的培训" | td_get_employee_training | employee_id=3, status="进行中" | 仅返回进行中的培训 |

### 1.3 九宫格盘点 `td_get_employee_talent_review`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-07 | "张三的人才盘点结果" | td_get_employee_talent_review | employee_id=1 | 返回九宫格历史 |
| TD-08 | "李四 2024 年的盘点情况" | td_get_employee_talent_review | employee_id=2, review_year=2024 | 按年度过滤 |
| TD-09 | "赵六历年九宫格标签" | td_get_employee_talent_review | employee_id=4 | 返回多年记录 |

### 1.4 个人发展计划 `td_get_employee_idp`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-10 | "张三的 IDP 完成情况" | td_get_employee_idp | employee_id=1 | 返回 IDP 列表含 progress |
| TD-11 | "看看王五 2025 年的发展计划" | td_get_employee_idp | employee_id=3, plan_year=2025 | 按年度过滤 |
| TD-12 | "陈小红有没有个人发展计划" | td_get_employee_idp | employee_id=5 | 空结果无异常 |

### 1.5 绩效详情 `td_get_employee_performance`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-13 | "张三的绩效考评详情" | td_get_employee_performance | employee_id=1 | 返回含评分和评语 |
| TD-14 | "看看马骏历次绩效" | td_get_employee_performance | employee_id=16 | 包含多期记录 |

### 1.6 岗位变动履历 `td_get_employee_history`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-15 | "张三的岗位变动记录" | td_get_employee_history | employee_id=1 | 含入职/晋升/调岗 |
| TD-16 | "李四的履历变动" | td_get_employee_history | employee_id=2 | 时间有序 |

### 1.7 考勤记录 `td_get_employee_attendance`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-17 | "张三最近的考勤记录" | td_get_employee_attendance | employee_id=1 | 返回考勤数据 |
| TD-18 | "李四 2025 年 1 月的考勤" | td_get_employee_attendance | employee_id=2, start_date="2025-01-01", end_date="2025-01-31" | 日期区间过滤 |

---

## 二、新增数据维度查询（4 个工具）

### 2.1 技能标签 `td_get_employee_skills`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-19 | "张三有哪些技能" | td_get_employee_skills | employee_id=1 | 返回技能列表含 level |
| TD-20 | "看看李四的技术类技能" | td_get_employee_skills | employee_id=2, category="技术" | 按分类过滤 |
| TD-21 | "王五的管理能力标签" | td_get_employee_skills | employee_id=3, category="管理" | 仅返回管理类 |

### 2.2 教育背景 `td_get_employee_education`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-22 | "张三的学历" | td_get_employee_education | employee_id=1 | 含学位、专业、院校 |
| TD-23 | "赵六是什么学校毕业的" | td_get_employee_education | employee_id=4 | 有本科+硕士两条 |

### 2.3 项目经历 `td_get_employee_projects`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-24 | "张三参与过哪些项目" | td_get_employee_projects | employee_id=1 | 返回项目列表 |
| TD-25 | "李四作为负责人的项目" | td_get_employee_projects | employee_id=2, role="负责人" | 按角色过滤 |

### 2.4 证书认证 `td_get_employee_certificates`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-26 | "张三有什么证书" | td_get_employee_certificates | employee_id=1 | 返回证书列表 |
| TD-27 | "看看李四的专业技术认证" | td_get_employee_certificates | employee_id=2, category="专业技术" | 按分类过滤 |

---

## 三、分析报表（6 个工具）

### 3.1 培训统计 `td_training_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-28 | "各部门培训完成率" | td_training_summary | year=None | 返回各部门统计 |
| TD-29 | "2024 年各部门培训情况" | td_training_summary | year=2024 | 按年度过滤 |

### 3.2 九宫格分布 `td_nine_grid_distribution`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-30 | "公司九宫格分布怎样" | td_nine_grid_distribution | 无过滤 | 返回全公司分布 |
| TD-31 | "后端组的高潜人才有哪些" | td_nine_grid_distribution | department_id=7 | 按部门过滤，含高潜清单 |
| TD-32 | "2024 年盘点的九宫格分布" | td_nine_grid_distribution | review_year=2024 | 按年度过滤 |

### 3.3 绩效分布 `td_performance_distribution`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-33 | "各部门绩效评级分布" | td_performance_distribution | 无过滤 | 返回 A/B+/B/C/D 占比 |
| TD-34 | "2024 年下半年绩效分布" | td_performance_distribution | year=2024, half="H2" | 按半年度过滤 |

### 3.4 人员流动分析 `td_turnover_analysis`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-35 | "各部门离职率如何" | td_turnover_analysis | 无参数 | 含离职率/转正率/平均司龄 |
| TD-36 | "公司人员流动分析" | td_turnover_analysis | 无参数 | 同上 |

### 3.5 晋升统计 `td_promotion_stats`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-37 | "去年各部门晋升了多少人" | td_promotion_stats | year=None（默认上一年） | 返回晋升/调岗数 |
| TD-38 | "2024 年晋升统计" | td_promotion_stats | year=2024 | 按年度过滤 |

### 3.6 IDP 汇总 `td_idp_summary`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-39 | "公司 IDP 完成情况怎样" | td_idp_summary | plan_year=None | 含完成率/目标分布/平均进度 |
| TD-40 | "2025 年 IDP 达成率" | td_idp_summary | plan_year=2025 | 按年度过滤 |

---

## 四、人才发现（6 个工具）

### 4.1 被埋没高潜 `td_discover_hidden_talent`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-41 | "公司有没有被低估的员工" | td_discover_hidden_talent | department_id=None | 返回全公司候选 |
| TD-42 | "后端组谁被埋没了" | td_discover_hidden_talent | department_id=7 | 按部门过滤 |
| TD-43 | "哪些人绩效好但标签低" | td_discover_hidden_talent | department_id=None | 理解语义映射到正确工具 |

### 4.2 流失风险 `td_assess_flight_risk`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-44 | "哪些优秀员工有流失风险" | td_assess_flight_risk | department_id=None | 返回风险预警 |
| TD-45 | "AI 组有人可能要离职吗" | td_assess_flight_risk | department_id=9 | 按部门过滤 |
| TD-46 | "最近要重点关注哪些人的留任" | td_assess_flight_risk | department_id=None | 语义理解准确 |

### 4.3 晋升准备度 `td_promotion_readiness`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-47 | "评估张三的晋升准备度" | td_promotion_readiness | employee_id=1 | 单人评估 |
| TD-48 | "后端组谁最适合晋升" | td_promotion_readiness | department_id=7 | 部门全员评估，降序排列 |
| TD-49 | "全公司晋升准备度排名" | td_promotion_readiness | 两者均 None | 全员评估 |

### 4.4 岗位适配 `td_find_candidates`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-50 | "推荐适合做 Python 后端的人" | td_find_candidates | requirements="Python" 或 "Python,后端" | 匹配结果含 Python 技能 |
| TD-51 | "谁适合做项目管理" | td_find_candidates | requirements="项目管理" | 匹配管理相关技能 |
| TD-52 | "找会 Python、Docker、K8s 的人" | td_find_candidates | requirements="Python,Docker,K8s" 或类似 | 多关键词匹配 |

### 4.5 人才画像 `td_talent_portrait`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-53 | "给我张三的完整人才画像" | td_talent_portrait | employee_id=1 | 全维度数据汇总 |
| TD-54 | "全方位了解一下李四" | td_talent_portrait | employee_id=2 | 语义理解映射正确 |

### 4.6 团队能力短板 `td_team_capability_gap`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| TD-55 | "分析后端组的能力短板" | td_team_capability_gap | department_id=7 | 返回技能覆盖+缺口 |
| TD-56 | "AI 组缺什么能力" | td_team_capability_gap | department_id=9 | 含稀缺技能+建议 |

---

## 五、权限测试

| ID | 场景 | session_state | 用户输入 | 预期结果 |
|----|------|-------------|---------|---------|
| AUTH-01 | talent_dev 正常访问 | roles=["talent_dev"] | "张三的绩效详情" | 正常返回数据 |
| AUTH-02 | 普通员工越权 | roles=[] | "张三的绩效详情" | 返回"该功能仅限人才发展角色使用" |
| AUTH-03 | manager 越权 | roles=["manager"] | "给我李四的人才画像" | 返回权限不足提示 |
| AUTH-04 | admin 越权 | roles=["admin"] | "公司九宫格分布" | 返回权限不足提示 |
| AUTH-05 | 多角色含 talent_dev | roles=["manager","talent_dev"] | "哪些人有流失风险" | 正常返回数据 |
| AUTH-06 | 权限错误后不重试 | roles=[] | "帮我分析后端组能力短板" | Agent 收到权限错误后不再调用 td_ 工具 |

---

## 六、工具选择歧义测试

验证 Agent 在语义近似时选择正确工具。

| ID | 用户输入 | 期望工具 | 不应调用 | 说明 |
|----|---------|---------|---------|------|
| AMB-01 | "张三的个人信息" | td_get_employee_profile | get_employee_info | talent_dev 应用 td_ 前缀工具 |
| AMB-02 | "看看张三这几年的绩效走势" | td_get_employee_performance | td_promotion_readiness | 查绩效详情，非晋升评估 |
| AMB-03 | "张三适不适合晋升" | td_promotion_readiness | td_get_employee_performance | 晋升准备度评估，非单纯查绩效 |
| AMB-04 | "后端组培训做得怎么样" | td_training_summary | td_get_employee_training | 部门级汇总，非个人培训查询 |
| AMB-05 | "公司人才盘点结果" | td_nine_grid_distribution | td_get_employee_talent_review | 全公司分布，非个人盘点 |
| AMB-06 | "帮我找做过大模型项目的人" | td_find_candidates | td_get_employee_projects | 岗位匹配推荐，非查个人项目 |
| AMB-07 | "张三有什么发展建议" | td_talent_portrait 或 td_get_employee_idp | td_discover_hidden_talent | 个人维度，非发现场景 |

---

## 七、多工具组合测试

验证 Agent 能正确组合多个工具完成复杂查询。

| ID | 用户输入 | 期望工具组合 | 验证点 |
|----|---------|------------|--------|
| COMBO-01 | "对比张三和李四的绩效" | td_get_employee_performance ×2 | 分别查两人后对比 |
| COMBO-02 | "后端组谁最适合晋升，给我他的完整画像" | td_promotion_readiness → td_talent_portrait | 先评估排名再查画像 |
| COMBO-03 | "AI 组缺什么能力，推荐匹配人选" | td_team_capability_gap → td_find_candidates | 先分析缺口再推荐 |
| COMBO-04 | "张三绩效怎么样，他的 IDP 完成了吗" | td_get_employee_performance + td_get_employee_idp | 两个独立查询 |
| COMBO-05 | "列出有流失风险的人，给每个人出画像" | td_assess_flight_risk → td_talent_portrait ×N | 先预警再逐人画像 |

---

## 八、边界与异常

| ID | 场景 | 用户输入 | 预期行为 |
|----|------|---------|---------|
| EDGE-01 | 员工不存在 | "查一下工号 999 的技能" | 返回空结果或友好提示 |
| EDGE-02 | 部门不存在 | "分析部门 999 的能力短板" | 返回空结果，无异常 |
| EDGE-03 | 非 HR 问题 | "帮我订个会议室" | Agent 告知不在 HR 服务范围 |
| EDGE-04 | 无技能数据 | "新员工罗敏有什么技能" | 返回空列表 |
| EDGE-05 | 年份不合理 | "2030 年的绩效分布" | 返回空数据，无异常 |
| EDGE-06 | 模糊员工姓名 | "小张的绩效" | Agent 应确认具体是哪位员工或匹配"张三" |
