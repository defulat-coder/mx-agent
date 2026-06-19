# 人才发现引擎 — 测试评估

## 一、测试范围

| 模块 | 文件 | 职责 |
|------|------|------|
| Schema | `app/schemas/discovery.py` | 6 个场景的请求/响应结构 |
| Service | `app/services/discovery.py` | 规则筛选 + 数据聚合（581 行核心逻辑） |
| Tools | `app/tools/hr/discovery.py` | 6 个 Agent Tool（权限校验 + session 管理） |
| Tools | `app/tools/hr/talent_dev_query.py` | 17 个人才发展查询工具 |
| Models | `app/models/hr/{skill,education,project_experience,certificate}.py` | 4 个新数据模型 |
| 种子数据 | `scripts/generate_seed.py` / `scripts/seed.sql` | 20 人 × 16 张表测试数据 |

---

## 二、测试场景与用例

### 场景 1：被埋没高潜识别 (`discover_hidden_talent`)

**业务规则**：
1. 连续最近 2 期绩效 ≥ B+（A 或 B+）
2. 自主报名（`assigned_by == ""`）且已完成的培训 ≥ 3
3. IDP 完成率 > 70%
4. 九宫格标签为「普通」或「无」，或九宫格位置为「中坚/待雕琢/专家/待观察/淘汰区/无」

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| HT-01 | 全公司扫描 | `department_id=None` | 返回 `HiddenTalentResult`，候选人均满足 4 条规则 | total 与 candidates 长度一致 |
| HT-02 | 按部门过滤 | `department_id=7`（后端组） | 仅返回后端组员工（张三/李四/陈小红/马骏） | 候选人 department_id 全为 7 |
| HT-03 | 空部门 | `department_id=999` | `HiddenTalentResult(candidates=[], total=0)` | 无异常抛出 |
| HT-04 | 绩效不足2期 | 新入职员工（如 id=19 罗敏，试用期） | 不出现在候选中 | `len(emp_perfs) < 2` 被跳过 |
| HT-05 | 最近2期非连续优秀 | 若最近2期为 [B, A]，则 B 不在 good_ratings | 不出现在候选中 | consecutive_good < 2 |
| HT-06 | 自主培训不足 | 自主完成培训 < 3 的员工 | 不出现在候选中 | 校验 `assigned_by == ""` 且 `status == "已完成"` |
| HT-07 | IDP 完成率 ≤ 70% | IDP 全为「进行中」的员工 | 不出现在候选中 | `completed / total <= 0.7` |
| HT-08 | 九宫格标签为高潜 | 标签为「高潜」且位置为「明星」 | 不出现在候选中 | `current_tag not in low_tags and current_pos not in low_positions` |
| HT-09 | signals 内容完整性 | 满足条件的候选人 | signals 包含绩效、培训数、IDP 完成率、标签信息 | ≥ 3 条 signal |
| HT-10 | performance_trend 正确性 | 满足条件的候选人 | 返回最近 ≤ 4 期的评级列表 | 列表长度 2-4，最后2项全为 A/B+ |

### 场景 2：流失风险预警 (`assess_flight_risk`)

**业务规则**：
1. 最新绩效 ∈ {A, B+}
2. 当前职级停留 ≥ 2 年
3. IDP 状态为「无」或「已放弃」（无活跃 IDP 且无已完成）
4. 统计近 3 个月加班时长

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| FR-01 | 全公司扫描 | `department_id=None` | 候选人均满足高绩效 + 职级停留 + IDP异常 | risk_signals 非空 |
| FR-02 | 按部门过滤 | `department_id=9`（AI 组） | 仅 AI 组员工 | 候选人 department 正确 |
| FR-03 | 低绩效排除 | 最新评级为 B/C/D 的员工 | 不出现在候选中 | latest_rating not in good_ratings |
| FR-04 | 职级停留 < 2年 | 新晋升员工（如 id=16 马骏 2024-06晋升 P6） | 不出现在候选中 | level_tenure < 2 |
| FR-05 | 有活跃 IDP | IDP status="进行中" 的员工 | 不出现在候选中 | idp_status == "进行中" 被跳过 |
| FR-06 | 无 IDP | 完全没有 IDP 的员工 | 出现在候选中（满足其他条件时） | idp_status == "无" |
| FR-07 | 加班疲劳预警 | 近3月加班 > 60h | risk_signals 包含疲劳提示 | `recent_ot_hours > 60` |
| FR-08 | 加班正常 | 近3月加班 ≤ 60h | risk_signals 无疲劳提示 | 仅有绩效和IDP两条 signal |
| FR-09 | 职级停留计算（有 history） | 有 employment_history 的员工 | 用最后一条 start_date 计算 | `(today - current_hist.start_date).days / 365.25` |
| FR-10 | 职级停留计算（无 history） | 无 history 时退回 hire_date | 用 hire_date 计算 | 逻辑分支覆盖 |

### 场景 3：晋升准备度评估 (`evaluate_promotion_readiness`)

**评分规则**：
- 职级停留(25%): `min(tenure/2 * 100, 100)` — 2年及以上满分
- 绩效(30%): A=100, B+=80, B=60, C=30, D=0
- 管理培训(20%): `min(count/3 * 100, 100)` — 3门及以上满分
- IDP进度(25%): 各 IDP 平均 progress

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| PR-01 | 单人评估 | `employee_id=1` | 返回张三一人的评估 | items 长度 1 |
| PR-02 | 部门评估 | `department_id=7` | 返回后端组全员 | items 按 readiness_score 降序 |
| PR-03 | 全公司评估 | 两者均为 None | 返回全部在职员工 | items 数 = 活跃员工数 |
| PR-04 | 不存在的员工 | `employee_id=999` | `PromotionReadinessResult(items=[])` | 空结果无异常 |
| PR-05 | 评分范围 | 任意员工 | readiness_score ∈ [1, 100] | `max(1, min(100, ...))` |
| PR-06 | 绩效评分映射 | A/B+/B/C/D 各自映射 | 对应 100/80/60/30/0 | rating_scores dict 覆盖 |
| PR-07 | 无绩效记录 | 无 performance_review 的员工 | latest_rating 默认 "B"，perf_score=60 | 缺省值逻辑 |
| PR-08 | 管理培训过滤 | 仅统计 `category=="管理能力"` 且 `status=="已完成"` | 非管理类或未完成不计入 | SQL 过滤条件 |
| PR-09 | IDP 进度平均值 | 多个 IDP | avg_progress = sum(progress) / count | 分母为 max(len, 1) |
| PR-10 | 排序验证 | 部门评估 | items[0].readiness_score >= items[-1].readiness_score | 降序排列 |

### 场景 4：岗位适配推荐 (`find_candidates`)

**匹配规则**：
- 技能匹配: `10 × level_bonus`（专家=4, 高级=3, 中级=2, 初级=1）
- 项目匹配: `5 × role_bonus`（负责人=3, 核心成员=2, 参与者=1）
- 培训匹配: 2 分
- 绩效 C/D 排除，返回 Top 20

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| CM-01 | 单关键词 | `requirements="Python"` | 返回有 Python 技能的员工 | matched_skills 包含 Python |
| CM-02 | 多关键词 | `requirements="Python,Docker,Kubernetes"` | 匹配度高的排前面 | 按 score 降序 |
| CM-03 | 中文逗号分隔 | `requirements="Python，机器学习"` | 正确拆分关键词 | `replace("，", ",")` 处理 |
| CM-04 | 顿号分隔 | `requirements="NLP、大模型应用"` | 正确拆分 | `replace("、", ",")` 处理 |
| CM-05 | 空格分隔退化 | `requirements="Python Docker"` | 按空格拆分 | `requirements.split()` |
| CM-06 | 无匹配 | `requirements="COBOL"` | candidates=[], total=0 | score=0 全部跳过 |
| CM-07 | 绩效排除 | 最新绩效为 C/D 的员工 | 不出现在候选中 | `latest_rating in ("C", "D")` |
| CM-08 | 技能等级权重 | 同一技能不同等级 | 专家得分 > 高级 > 中级 > 初级 | level_bonus 乘积 |
| CM-09 | 项目角色权重 | 同一项目不同角色 | 负责人得分 > 核心成员 > 参与者 | role_bonus 乘积 |
| CM-10 | Top 20 截断 | 匹配人数 > 20（构造场景） | 最多返回 20 人 | `scored[:20]` |
| CM-11 | 无技能数据提示 | 全员无技能标签 | notice 包含"技能数据不足" | 降级提示 |
| CM-12 | match_summary 内容 | 有技能和项目匹配 | summary 包含技能和项目信息 | `summary_parts` 非空 |

### 场景 5：人才画像 (`build_talent_portrait`)

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| TP-01 | 完整画像 | `employee_id=1`（张三） | 全部 10 个维度有数据 | 各 list 长度 > 0 |
| TP-02 | 新员工画像 | `employee_id=19`（罗敏，试用期） | 部分维度为空列表 | 无 certificate、少量 perf |
| TP-03 | 教育排序 | `employee_id=4`（本科+硕士） | 按 graduation_year 降序 | educations[0].graduation_year > [-1] |
| TP-04 | 技能分类排序 | 任意员工 | 按 category 排序 | skills 按 category 有序 |
| TP-05 | 项目按时间降序 | `employee_id=1` | 最新项目在前 | projects[0].start_date 最新 |
| TP-06 | 绩效按年半降序 | 任意员工 | year desc, half desc | 第一条为最新考评期 |
| TP-07 | 培训排序 | 任意员工 | 按 completed_date 降序（null 在后） | nullslast 逻辑 |
| TP-08 | 不存在员工 | `employee_id=999` | 应由 get_employee_info 抛异常或返回错误 | 异常处理 |

### 场景 6：团队能力短板分析 (`analyze_team_capability_gap`)

| 用例 ID | 用例描述 | 输入 | 预期结果 | 验证点 |
|---------|---------|------|---------|--------|
| TG-01 | 有技能数据部门 | `department_id=7`（后端组，4人有技能） | skill_coverage 非空，有 high_freq 和 rare | 统计正确 |
| TG-02 | 无员工部门 | `department_id=1`（马喜集团，无直属员工） | total_employees=0, notice="无在职员工" | 空部门处理 |
| TG-03 | 无技能数据降级 | 如果删除所有技能数据 | 基于培训推断，notice 包含"技能数据不足" | 降级逻辑 |
| TG-04 | 高频技能 | `department_id=7` | high_frequency_skills 最多 5 个 | `coverage[:5]` |
| TG-05 | 稀缺技能 | `department_id=7` | rare_skills 中每个技能仅 1 人掌握 | `count == 1` |
| TG-06 | 单点风险建议 | 有稀缺技能 | suggestions 包含"单点风险"提示 | `rare` 非空时触发 |
| TG-07 | 未录入技能建议 | 部分员工无技能标签 | suggestions 包含"尚未录入技能标签" | `emp_with_skills < len(employees)` |
| TG-08 | skill_coverage 排序 | 任意部门 | 按拥有人数降序 | coverage[0].count >= coverage[-1].count |
| TG-09 | levels 统计 | 某技能 | levels dict 各等级人数之和 = count | 数据一致性 |
| TG-10 | 不存在部门 | `department_id=999` | department_name="未知", total_employees=0 | dept 查询为 None 时 |

---

## 三、权限与安全测试

所有 6 个 discovery tools + 17 个 talent_dev_query tools 均需校验 `talent_dev` 角色。

| 用例 ID | 用例描述 | 输入 | 预期结果 |
|---------|---------|------|---------|
| AUTH-01 | talent_dev 角色调用 | session_state.roles=["talent_dev"] | 正常执行，返回 JSON |
| AUTH-02 | 普通员工调用 | session_state.roles=[] | 返回"该功能仅限人才发展角色使用" |
| AUTH-03 | manager 角色调用 | session_state.roles=["manager"] | 返回"该功能仅限人才发展角色使用" |
| AUTH-04 | admin 角色调用 | session_state.roles=["admin"] | 返回"该功能仅限人才发展角色使用" |
| AUTH-05 | 无登录态 | session_state=None | 注入模拟员工后校验角色 |
| AUTH-06 | 模拟员工 talent_dev | seed 命中 id=6 孙八 | 正常执行 |

---

## 四、数据模型测试

### 4.1 新增模型字段验证

| 模型 | 表名 | 关键验证 |
|------|------|---------|
| `Skill` | skills | employee_id FK, name 64字符, category ∈ {技术/管理/业务/通用}, level ∈ {初级/中级/高级/专家}, source ∈ {自评/上级评/认证}, verified bool |
| `Education` | educations | employee_id FK, degree 16字符, major 64字符, school 128字符, graduation_year int |
| `ProjectExperience` | project_experiences | employee_id FK, role ∈ {负责人/核心成员/参与者}, end_date 可为 NULL（进行中项目） |
| `Certificate` | certificates | employee_id FK, expiry_date 可为 NULL（终身有效）, category ∈ {专业技术/管理/语言/行业} |

### 4.2 种子数据覆盖度

| 数据表 | 记录数 | 覆盖员工数 | 备注 |
|--------|--------|-----------|------|
| skills | ~90 | 20/20 | 每人 3-6 个技能 |
| educations | 27 | 20/20 | 部分员工有硕士/MBA |
| project_experiences | 22 | 10/20 | 非所有人有项目 |
| certificates | 16 | 10/20 | 非所有人有证书 |

---

## 五、边界与异常测试

| 用例 ID | 场景 | 预期行为 |
|---------|------|---------|
| EDGE-01 | 员工无绩效记录 | hidden_talent/flight_risk 跳过该员工 |
| EDGE-02 | 员工无 IDP | hidden_talent 跳过，flight_risk 中 idp_status="无" |
| EDGE-03 | 员工无 employment_history | 退回 hire_date 计算职级停留 |
| EDGE-04 | 员工 hire_date 为 None | tenure 计算为 0 |
| EDGE-05 | find_candidates 空关键词 | `requirements=""` → keywords 为空列表 → 全部 score=0 → 空结果 |
| EDGE-06 | find_candidates 特殊字符 | `requirements="Python>=3.13"` | 关键词包含特殊字符不报错 |
| EDGE-07 | 三月计算跨年 | 当 today.month ≤ 3 时的 three_months_ago 计算 | `date(today.year - 1, today.month + 9, 1)` |
| EDGE-08 | IDP progress=0 | 所有 IDP 进度为 0 | 晋升准备度 IDP 分项为 0 |
| EDGE-09 | 部门无技能也无培训 | 新建空部门 | capability_gap 返回空 suggestions |
| EDGE-10 | 并发调用 | 多个 discovery tool 同时执行 | async session 互不干扰 |

---

## 六、集成测试（Agent → Tool → Service → DB）

| 用例 ID | 场景 | 验证方式 |
|---------|------|---------|
| INT-01 | HR Agent 调用 discover_hidden_talent | 通过 Agent chat 发送"哪些员工可能被低估了" |
| INT-02 | HR Agent 调用 assess_flight_risk | "哪些优秀员工有流失风险" |
| INT-03 | HR Agent 调用 promotion_readiness | "评估后端组晋升准备度" |
| INT-04 | HR Agent 调用 find_candidates | "推荐适合做 Python 后端开发的人选" |
| INT-05 | HR Agent 调用 talent_portrait | "给我张三的完整人才画像" |
| INT-06 | HR Agent 调用 team_capability_gap | "分析 AI 组的能力短板" |
| INT-07 | 非 talent_dev 用户触发 | 普通员工问"公司谁有流失风险" → 返回权限不足 |
| INT-08 | Tool 返回 JSON 可解析 | model_dump_json() 输出可被前端正确解析 |

---

## 七、性能基准

| 指标 | 基准值 | 说明 |
|------|--------|------|
| discover_hidden_talent（20人） | < 500ms | 4 次批量查询 + 逐人计算 |
| assess_flight_risk（20人） | < 500ms | 4 次批量查询 |
| evaluate_promotion_readiness（20人） | < 500ms | 4 次批量查询 |
| find_candidates（20人） | < 500ms | 4 次批量查询 + 关键词匹配 |
| build_talent_portrait（单人） | < 300ms | 9 次单人查询 |
| analyze_team_capability_gap（单部门） | < 300ms | 2-3 次查询 |

---

## 八、已知风险点

| # | 风险 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | `assess_flight_risk` 三月计算 bug | 高 | `today.month - 3` 当 month=1,2,3 时，`max(today.month - 3, 1)` 结果为 1，不会走 else 分支。实际 month=3 时 `3-3=0`，`max(0,1)=1` 即 1 月 1 日，正确。month=1 时 `1-3=-2`，`max(-2,1)=1` 即当年 1 月 1 日，仅覆盖 1 个月而非 3 个月。**建议修复** |
| 2 | `discover_hidden_talent` 自主培训判定 | 中 | `assigned_by == ""` 空字符串判定，数据库可能存 NULL | 需确认 ORM 默认值 |
| 3 | `find_candidates` 关键词大小写 | 低 | 已做 `.lower()` 处理，但中文关键词无需此步骤 |
| 4 | `build_talent_portrait` 无异常处理 | 中 | employee_id 不存在时 `get_employee_info` 行为未明确 |
| 5 | 绩效数据随机生成 | 低 | seed=42 固定种子，但测试用例依赖具体值需预计算 |
