# 行政助手 — Agent 评估用例

> 角色：员工（所有用户）+ 行政人员（`roles: ["admin_staff"]`）
> 工具集：9 个员工工具 + 9 个行政人员工具，共 18 个
> Skills：3 个知识库（travel-policy / office-rules / meeting-room-rules）
> 种子数据：10 会议室 + 30 预订 + 15 用品 + 15 申领 + 15 快递 + 15 访客

---

## 一、路由识别（Router Team → Admin Agent）

| ID | 用户输入 | 预期路由 | 验证点 |
|----|---------|---------|--------|
| RT-01 | "帮我订个会议室" | Admin Assistant | 识别为行政会议室预订 |
| RT-02 | "我想领一些签字笔" | Admin Assistant | 识别为行政用品申领 |
| RT-03 | "有我的快递吗" | Admin Assistant | 识别为行政快递查询 |
| RT-04 | "我要预约一个访客来访" | Admin Assistant | 识别为行政访客预约 |
| RT-05 | "差旅标准是什么" | Admin Assistant | 识别为行政制度咨询 |
| RT-06 | "我这个月工资多少" | HR Assistant | 不应路由到行政 |
| RT-07 | "电脑坏了" | IT Assistant | 不应路由到行政 |

---

## 二、员工自助 — 会议室（3 个工具）

### 2.1 查询可用会议室 `adm_get_available_rooms`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EQ-01 | "查看可用的会议室" | adm_get_available_rooms | 无 | 返回可用会议室列表 |
| EQ-02 | "明天下午 2 点到 3 点有空的会议室" | adm_get_available_rooms | date, start_time, end_time | 返回该时段无冲突的会议室 |
| EQ-03 | "有能坐 10 个人的会议室吗" | adm_get_available_rooms | capacity≥10 | 返回容量满足的会议室 |

### 2.2 预订会议室 `adm_book_room`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EA-01 | "帮我预订 3 号会议室，明天 10:00-11:00" | adm_book_room | room_id=3, date, start_time, end_time | 30 分钟槽位制，生成预订记录 |
| EA-02 | "预订一个已被占用的时段" | adm_book_room | 冲突时段 | 返回时间冲突提示 |
| EA-03 | "预订 10:15 开始的会议" | adm_book_room | 非 30 分钟对齐 | 返回时间必须为 30 分钟整数倍 |

### 2.3 取消预订 `adm_cancel_booking`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EA-04 | "取消我明天的会议室预订" | adm_cancel_booking | booking_id | 预订状态变为 cancelled |
| EA-05 | "取消别人的预订" | adm_cancel_booking | 非本人 booking | 返回权限不足 |

### 2.4 我的预订 `adm_get_my_bookings`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| EQ-04 | "查看我的会议室预订" | adm_get_my_bookings | 返回当前用户的预订列表 |

---

## 三、员工自助 — 用品/快递/访客/差旅（5 个工具）

### 3.1 申领用品 `adm_request_supply`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EA-06 | "我要领 5 支签字笔" | adm_request_supply | supply_id, quantity=5 | 创建申领单，status=pending |
| EA-07 | "领 100 支笔" | adm_request_supply | quantity=100 | 库存不足时返回提示 |

### 3.2 快递查询 `adm_get_my_express`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| EQ-05 | "有我的快递吗" | adm_get_my_express | 返回当前用户的快递列表 |
| EQ-06 | "查看我已签收的快递" | adm_get_my_express | status="received" 筛选 |

### 3.3 访客预约 `adm_book_visitor`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| EA-08 | "帮我预约一个访客，张三，明天上午来" | adm_book_visitor | visitor_name, visit_date | 创建访客预约记录 |

### 3.4 我的访客 `adm_get_my_visitors`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| EQ-07 | "查看我预约的访客" | adm_get_my_visitors | 返回当前用户预约的访客列表 |

### 3.5 差旅申请 `adm_apply_travel`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| EA-09 | "我要出差，帮我申请差旅" | adm_apply_travel | 返回 OA 审批链接 |

---

## 四、Skills 知识库咨询（3 个 Skills）

### 4.1 差旅制度 `travel-policy`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-01 | "出差住宿标准是多少" | 使用 travel-policy Skill | 包含住宿标准按职级划分 |
| SK-02 | "出差可以坐高铁商务座吗" | 使用 travel-policy Skill | 包含交通标准规定 |
| SK-03 | "差旅餐费标准" | 使用 travel-policy Skill | 包含餐费补贴标准 |

### 4.2 办公规范 `office-rules`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-04 | "办公用品怎么领" | 使用 office-rules Skill | 包含申领流程和审批要求 |
| SK-05 | "工位管理有什么规定" | 使用 office-rules Skill | 包含工位使用规范 |

### 4.3 会议室规范 `meeting-room-rules`

| ID | 用户输入 | 期望行为 | 验证点 |
|----|---------|---------|--------|
| SK-06 | "会议室预订规则是什么" | 使用 meeting-room-rules Skill | 包含预订/取消/超时规则 |
| SK-07 | "会议室迟到多久会被自动释放" | 使用 meeting-room-rules Skill | 包含超时释放规则 |

---

## 五、行政人员 — 预订管理（2 个工具）

### 5.1 全部预订查询 `adm_admin_get_all_bookings`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-01 | "查看所有会议室预订" | adm_admin_get_all_bookings | 无 | 返回全部预订记录 |
| AQ-02 | "查看今天 3 号会议室的预订" | adm_admin_get_all_bookings | room_id=3, date | 多条件筛选 |

### 5.2 释放会议室 `adm_admin_release_room`

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AA-01 | "把 5 号会议室设为维护状态" | adm_admin_release_room | room_id=5, status="maintenance" | 状态变为 maintenance |
| AA-02 | "恢复 5 号会议室" | adm_admin_release_room | room_id=5, status="available" | 状态恢复 available |

---

## 六、行政人员 — 用品/快递/访客（5 个工具）

### 6.1 申领单查询与审批

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-03 | "有哪些待审批的用品申领" | adm_admin_get_supply_requests | status="pending" | 返回待审批列表 |
| AA-03 | "通过申领单 3" | adm_admin_approve_supply | request_id=3, action="approve" | 状态→approved，库存自动扣减 |
| AA-04 | "拒绝申领单 5" | adm_admin_approve_supply | request_id=5, action="reject" | 状态→rejected |

### 6.2 库存查询 `adm_admin_get_supply_stock`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-04 | "办公用品库存情况" | adm_admin_get_supply_stock | 返回全部用品库存列表 |

### 6.3 快递管理

| ID | 用户输入 | 期望工具 | 关键参数 | 验证点 |
|----|---------|---------|---------|--------|
| AQ-05 | "查看所有未签收的快递" | adm_admin_get_all_express | status="pending" | 返回未签收快递 |
| AA-05 | "登记一个快递给张三" | adm_admin_register_express | employee_id, tracking_no | 创建快递记录 |

### 6.4 访客管理 `adm_admin_get_visitors`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-06 | "今天有哪些访客" | adm_admin_get_visitors | 返回今日访客列表 |

### 6.5 统计 `adm_admin_usage_stats`

| ID | 用户输入 | 期望工具 | 验证点 |
|----|---------|---------|--------|
| AQ-07 | "行政综合统计" | adm_admin_usage_stats | 返回会议室使用率/用品消耗/快递量 |

---

## 七、权限校验

| ID | 场景 | 用户输入 | 测试用户 | 期望结果 |
|----|------|---------|---------|---------|
| PR-01 | 员工调管理员工具 | "查看所有预订" | 普通员工 | 返回权限不足 |
| PR-02 | 员工调管理员工具 | "审批申领单 1" | 普通员工 | 返回权限不足 |

---

## 八、边界与异常场景

| ID | 场景 | 用户输入 | 期望行为 |
|----|------|---------|---------|
| EX-01 | 超出范围 | "帮我查薪资" | 告知不在行政范围，建议联系 HR |
| EX-02 | 模糊意图 | "帮我预约" | 追问是预约会议室还是访客 |
| EX-03 | Skills → 操作 | "差旅标准是什么？那帮我申请" | 先查 Skill 回答制度，再调 adm_apply_travel |
| EX-04 | 多轮对话 | 先"订会议室"→追问时间/房间→确认预订 | 分步收集信息后调用工具 |
| EX-05 | 不存在的资源 | "预订 99 号会议室" | 返回会议室不存在 |

---

## 九、评估统计

| 维度 | 数量 |
|------|------|
| 路由识别 | 7 |
| 员工会议室 | 8 |
| 员工其他 | 9 |
| Skills 咨询 | 7 |
| 管理员预订 | 4 |
| 管理员其他 | 9 |
| 权限校验 | 2 |
| 边界异常 | 5 |
| **合计** | **51** |
