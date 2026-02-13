# IT 运维助手 — Agent 评估用例

> 角色：员工（所有用户）+ IT 管理员（`roles: ["it_admin"]`）
> 工具集：4 个员工工具 + 8 个管理员工具，共 12 个
> Skills：5 个知识库（wifi-vpn / printer / email / security / device-policy）
> 种子数据：30 设备 + 60 工单 + 15 流转记录

---

## 一、路由识别（Router Team → IT Agent）

| ID | 用户输入 | 预期路由 | 验证点 |
|----|---------|---------|--------|
| RT-01 | "我的电脑开不了机" | IT Assistant | 识别为 IT 报修场景 |
| RT-02 | "WiFi 连不上怎么办" | IT Assistant | 识别为 IT 网络问题 |
| RT-03 | "帮我重置邮箱密码" | IT Assistant | 识别为 IT 密码重置 |
| RT-04 | "我想申请安装 Docker" | IT Assistant | 识别为 IT 软件安装 |
| RT-05 | "查一下我的设备" | IT Assistant | 识别为 IT 设备查询 |
| RT-06 | "我这个月工资多少" | HR Assistant | 不应路由到 IT |
| RT-07 | "我的 IT 工单进度怎么样" | IT Assistant | 识别为 IT 工单查询 |

---

## 二、员工自助 — 工单查询（3 个工具）

### 2.1 我的工单列表 `it_get_my_tickets`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-01 | "查看我的 IT 工单" | it_get_my_tickets | 无 | 返回当前用户提交的工单列表 |
| EQ-02 | "我有哪些还没处理的工单" | it_get_my_tickets | status="open" | 仅返回 open 状态 |
| EQ-03 | "看看我已解决的 IT 工单" | it_get_my_tickets | status="resolved" | 仅返回 resolved 状态 |

### 2.2 工单详情 `it_get_ticket_detail`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-04 | "查看工单 5 的详情" | it_get_ticket_detail | ticket_id=5 | 返回完整工单信息含 description/resolution |
| EQ-05 | "工单 IT-T-0010 什么情况了" | it_get_ticket_detail | ticket_id=10 | 正确识别工单编号→ID |
| EQ-06 | "查看工单 9999" | it_get_ticket_detail | ticket_id=9999 | 返回工单不存在提示 |

### 2.3 我的设备 `it_get_my_assets`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-07 | "我名下有什么设备" | it_get_my_assets | 无 | 返回当前用户名下的在用设备 |
| EQ-08 | "查看我的电脑信息" | it_get_my_assets | 无 | 返回含 asset_no/brand/model_name |
| EQ-09 | "我的设备保修到什么时候" | it_get_my_assets | 无 | 返回含 warranty_expire 字段 |

---

## 三、员工自助 — 工单创建（1 个工具）

### 3.1 创建工单 `it_create_ticket`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EA-01 | "我的笔记本无法开机，帮我报修" | it_create_ticket | type="repair", title 含"无法开机" | 生成 ticket_no，status=open |
| EA-02 | "邮箱密码忘了，帮我重置" | it_create_ticket | type="password_reset" | type 正确识别 |
| EA-03 | "我要申请安装 Figma" | it_create_ticket | type="software_install" | type 正确识别 |
| EA-04 | "申请 GitLab 仓库权限" | it_create_ticket | type="permission" | type 正确识别 |
| EA-05 | "电脑很卡，而且经常蓝屏，很急" | it_create_ticket | type="repair", priority="high" 或 "urgent" | 从描述中推断高优先级 |
| EA-06 | "帮我报修一下" | — | — | Agent 应追问具体问题再创建工单，不直接调用 |

---

## 四、Skills 知识库咨询（5 个 Skills）

### 4.1 WiFi/VPN 排查 `wifi-vpn`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-01 | "WiFi 连不上怎么办" | 使用 wifi-vpn Skill 回答 | 包含排查步骤（忘记网络/重连/DNS） |
| SK-02 | "VPN 连接失败" | 使用 wifi-vpn Skill 回答 | 包含 VPN 服务器地址和排查步骤 |
| SK-03 | "公司 WiFi 密码是什么" | 使用 wifi-vpn Skill 回答 | 说明使用 AD 账号认证，无单独密码 |

### 4.2 打印机 `printer`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-04 | "怎么安装打印机" | 使用 printer Skill 回答 | 包含 IP 地址和安装步骤 |
| SK-05 | "打印机卡纸了" | 使用 printer Skill 回答 | 包含卡纸处理步骤 |

### 4.3 邮箱 `email`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-06 | "怎么在手机上配置公司邮箱" | 使用 email Skill 回答 | 包含 Outlook App 配置步骤 |
| SK-07 | "收不到邮件" | 使用 email Skill 回答 | 包含检查垃圾邮件/容量等步骤 |

### 4.4 信息安全 `security`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-08 | "公司密码策略是什么" | 使用 security Skill 回答 | 包含 8 位/90 天/复杂度要求 |
| SK-09 | "可以用自己的 U 盘吗" | 使用 security Skill 回答 | 说明仅允许公司加密 U 盘 |
| SK-10 | "收到可疑邮件怎么办" | 使用 security Skill 回答 | 包含安全事件上报流程 |

### 4.5 设备管理 `device-policy`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-11 | "设备借用需要什么流程" | 使用 device-policy Skill 回答 | 包含创建工单+主管审批+30 天期限 |
| SK-12 | "离职需要归还设备吗" | 使用 device-policy Skill 回答 | 包含归还流程和数据清除要求 |

---

## 五、IT 管理员 — 工单管理（3 个工具）

### 5.1 全部工单查询 `it_admin_get_tickets`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-01 | "查看所有待处理的工单" | it_admin_get_tickets | status="open" | 仅返回 open 状态工单 |
| AQ-02 | "有哪些紧急工单" | it_admin_get_tickets | priority="urgent" | 仅返回 urgent 优先级 |
| AQ-03 | "查看所有报修类工单" | it_admin_get_tickets | type="repair" | 仅返回 repair 类型 |
| AQ-04 | "查看所有工单" | it_admin_get_tickets | 无筛选 | 返回全部工单列表 |
| AQ-05 | "有没有高优先级的密码重置工单" | it_admin_get_tickets | type="password_reset", priority="high" | 多条件筛选生效 |

### 5.2 工单处理 `it_admin_handle_ticket`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-01 | "受理工单 3" | it_admin_handle_ticket | ticket_id=3, action="accept" | status → in_progress，handler_id 设为当前管理员 |
| AA-02 | "工单 5 已经解决了，换了电源适配器" | it_admin_handle_ticket | ticket_id=5, action="resolve", resolution 含内容 | status → resolved，resolved_at 有值 |
| AA-03 | "关闭工单 10" | it_admin_handle_ticket | ticket_id=10, action="close" | status → closed |
| AA-04 | "处理工单 9999" | it_admin_handle_ticket | ticket_id=9999 | 返回工单不存在提示 |

### 5.3 权限校验

| ID | 用户输入 | 测试用户 | 期望结果 | 验证点 |
|----|---------|---------|---------|--------|
| AA-05 | "查看所有工单" | 普通员工（无 it_admin） | 返回权限不足提示 | 不泄露其他工单数据 |

---

## 六、IT 管理员 — 设备管理（3 个工具）

### 6.1 设备查询 `it_admin_get_assets`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AD-01 | "有哪些空闲设备" | it_admin_get_assets | status="idle" | 仅返回 idle 状态 |
| AD-02 | "查看所有笔记本" | it_admin_get_assets | type="laptop" | 仅返回 laptop 类型 |
| AD-03 | "查看全部设备资产" | it_admin_get_assets | 无筛选 | 返回 30 条记录 |

### 6.2 设备分配 `it_admin_assign_asset`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AD-04 | "把设备 ID 25 分配给员工 10" | it_admin_assign_asset | asset_id=25, employee_id=10 | status → in_use，写入 ITAssetHistory |
| AD-05 | "分配一台在用的设备给别人" | it_admin_assign_asset | 已在用的 asset_id | 返回"设备当前不可分配" |

### 6.3 设备回收 `it_admin_reclaim_asset`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AD-06 | "回收设备 ID 1" | it_admin_reclaim_asset | asset_id=1 | status → idle，employee_id=null，写入 ITAssetHistory |
| AD-07 | "回收一台空闲设备" | it_admin_reclaim_asset | idle 状态的 asset_id | 返回"设备当前未被使用" |

---

## 七、IT 管理员 — 统计报表（3 个工具）

### 7.1 工单统计 `it_admin_ticket_stats`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AS-01 | "给我看看工单统计" | it_admin_ticket_stats | 返回各状态/类型/优先级数量 + 平均处理时长 |
| AS-02 | "现在待处理的工单有多少" | it_admin_ticket_stats | by_status 含 open 计数 |

### 7.2 设备统计 `it_admin_asset_stats`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AS-03 | "设备资产统计情况" | it_admin_asset_stats | 返回各状态/类型数量 + 部门分配 |
| AS-04 | "各部门设备分配情况" | it_admin_asset_stats | by_department 含部门名称和数量 |

### 7.3 故障趋势 `it_admin_fault_trend`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AS-05 | "最近 3 个月的故障趋势" | it_admin_fault_trend | months=3 | 返回月度趋势 + TOP5 部门 |
| AS-06 | "半年的故障分析" | it_admin_fault_trend | months=6 | months 正确解析 |

---

## 八、边界与异常场景

| ID | 场景 | 用户输入 | 期望行为 |
|----|------|---------|---------|
| EX-01 | 超出范围 | "帮我订个会议室" | 告知不在 IT 服务范围，建议联系行政 |
| EX-02 | 模糊意图 | "我有个问题" | 追问具体问题，不盲目调用工具 |
| EX-03 | Skills → 工单 | "WiFi 排查完了还是连不上" | 在 Skills 排查指南之后建议创建工单 |
| EX-04 | 权限错误不重试 | 普通员工说"查看所有工单" | 调用 it_admin_get_tickets 返回权限不足后，不再重试 admin 工具 |
| EX-05 | 多轮对话 | 先"报修"→追问描述→确认创建 | 分步收集信息后调用 it_create_ticket |

---

## 九、评估统计

| 维度 | 数量 |
|------|------|
| 路由识别 | 7 |
| 员工查询 | 9 |
| 员工操作 | 6 |
| Skills 咨询 | 12 |
| 管理员工单 | 9 |
| 管理员设备 | 7 |
| 管理员统计 | 6 |
| 边界异常 | 5 |
| **合计** | **61** |
