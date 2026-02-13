# 马喜智能助手 (mx-agent)

基于 FastAPI + Agno 的企业级 AI 智能助手，支持 HR、IT 运维、行政、财务、法务等多领域智能问答与业务办理。

## 系统架构

```
┌───────────────────────────────────────────────────────────────────┐
│                          客户端层                                  │
│                   (Web / 移动端 / 第三方系统)                       │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      API 网关层 (FastAPI)                          │
│  ┌───────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐   │
│  │ RequestID │ │ 日志中间件 │ │ JWT 认证  │ │ 全局异常处理     │   │
│  └───────────┘ └──────────┘ └───────────┘ └──────────────────┘   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                     AgentOS 运行时 (Agno)                         │
│                                                                   │
│                      ┌─────────────────┐                          │
│                      │  Router Team    │ ← 智能路由 + 跨域协作      │
│                      │  (智能助手入口)   │                          │
│                      └───────┬─────────┘                          │
│       ┌──────────┼──────────┬──────────┬──────────┐         │
│       ▼          ▼          ▼          ▼          ▼         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌───────┐ │
│  │HR Agent │ │IT Agent │ │Admin    │ │Finance │ │ Legal │ │
│  │(已上线)  │ │(已上线)  │ │Agent   │ │Agent   │ │ Agent │ │
│  │55 Tools │ │12 Tools │ │(已上线)  │ │(已上线) │ │(已上线)│ │
│  │8 Skills │ │5 Skills │ │18 Tools │ │14 Tools│ │8 Tools│ │
│  │         │ │         │ │3 Skills │ │3 Skills│ │3 Skills│ │
│  └─────────┘ └─────────┘ └─────────┘ └────────┘ └───────┘ │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                          数据层                                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│  │ SQLite (业务)    │ │ SQLite (会话)    │ │ 外部系统         │     │
│  │ · 员工/部门      │ │ · 会话记忆       │ │ (HR审批系统)     │     │
│  │ · 考勤/薪资      │ │ · 追踪数据       │ │                 │     │
│  │ · 假期/社保      │ │                 │ │                 │     │
│  │ · IT设备/工单    │ │                 │ │                 │     │
│  │ · 会议室/预订    │ │                 │ │                 │     │
│  │ · 用品/快递/访客  │ │                 │ │                 │     │
│  │ · 报销/预算      │ │                 │ │                 │     │
│  │ · 应收/应付      │ │                 │ │                 │     │
│  │ · 合同/模板/审查  │ │                 │ │                 │     │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **Web 框架** | FastAPI + Uvicorn | RESTful API 服务 |
| **AI 框架** | Agno | 智能体编排与运行 |
| **LLM** | OpenAI API (GLM-4) | 大语言模型调用 |
| **ORM** | SQLAlchemy + aiosqlite | 异步数据库操作 |
| **配置** | Pydantic Settings | 环境变量管理 |
| **认证** | PyJWT | JWT Token 认证 |
| **日志** | Loguru | 结构化日志 |
| **可观测性** | OpenTelemetry + Agno Instrumentation | 链路追踪 |
| **依赖管理** | uv | Python 包管理 |

## 项目结构

```
app/
├── main.py                  # FastAPI + AgentOS 入口
├── config.py                # 环境变量配置
├── agents/                  # 智能体定义
│   ├── router_agent.py      #   路由智能体 (Team)
│   ├── hr_agent.py          #   HR 助手
│   ├── it_agent.py          #   IT 运维助手
│   ├── admin_agent.py       #   行政助手
│   ├── finance_agent.py     #   财务助手
│   └── legal_agent.py       #   法务助手
├── api/v1/                  # REST API 路由
├── core/                    # 基础设施
│   ├── database.py          #   数据库连接
│   ├── llm.py               #   LLM 配置
│   ├── masking.py           #   敏感数据脱敏
│   ├── middleware.py         #   中间件 (RequestID / 日志)
│   ├── exceptions.py        #   异常处理
│   ├── error_codes.py       #   错误码定义
│   ├── logging.py           #   日志配置
│   └── context.py           #   请求上下文
├── models/
│   ├── hr/                  #   HR ORM 模型 (16 张表)
│   ├── it/                  #   IT ORM 模型 (3 张表)
│   ├── admin/               #   行政 ORM 模型 (6 张表)
│   ├── finance/             #   财务 ORM 模型 (6 张表)
│   └── legal/               #   法务 ORM 模型 (3 张表)
├── schemas/                 # Pydantic 请求/响应 Schema
├── services/                # 业务逻辑层
├── skills/
│   ├── hr/                  #   HR Skills (8 个知识库)
│   ├── it/                  #   IT Skills (5 个知识库)
│   ├── admin/               #   行政 Skills (3 个知识库)
│   ├── finance/             #   财务 Skills (3 个知识库)
│   └── legal/               #   法务 Skills (3 个知识库)
├── tools/
│   ├── hr/                  #   HR Tools (55 个)
│   ├── it/                  #   IT Tools (12 个)
│   ├── admin/               #   行政 Tools (18 个)
│   ├── finance/             #   财务 Tools (14 个)
│   └── legal/               #   法务 Tools (8 个)
```

## 快速启动

```bash
# 克隆并安装依赖
uv sync

# 配置环境变量
cp .env.example .env  # 按需修改

# 启动服务
uv run python main.py
```

服务默认运行在 `http://localhost:8000`。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | 马喜智能助手 | 应用名称 |
| `API_PREFIX` | /v1 | API 路径前缀 |
| `DEBUG` | false | 调试模式 |
| `DATABASE_URL` | sqlite+aiosqlite:///data/mx_agent.db | 数据库连接 |
| `LLM_MODEL` | glm-4-plus | LLM 模型名称 |
| `LLM_API_KEY` | - | LLM API Key |
| `LLM_BASE_URL` | https://open.bigmodel.cn/api/paas/v4 | LLM API 地址 |
| `AUTH_SECRET` | - | JWT 签名密钥 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `LOG_FILE` | log/mx-agent.log | 日志文件路径 |
| `LOG_ROTATION` | 500 MB | 日志轮转大小 |
| `LOG_RETENTION` | 10 days | 日志保留时间 |

## 数据模型

### HR 模型（16 张表）

| 模型 | 说明 |
|------|------|
| `Employee` | 员工基本信息 |
| `Department` | 部门信息（树形结构） |
| `Attendance` | 考勤记录 |
| `LeaveBalance` | 假期余额 |
| `LeaveRequest` | 请假申请记录 |
| `Overtime` | 加班记录 |
| `SalaryRecord` | 月度薪资明细 |
| `SocialInsurance` | 社保公积金缴纳记录 |
| `PerformanceReview` | 绩效考评 |
| `EmploymentHistory` | 在职履历 |
| `Training` | 培训记录 |
| `TalentReview` | 人才盘点（九宫格） |
| `DevelopmentPlan` | 个人发展计划（IDP） |
| `Skill` | 技能标签 |
| `Education` | 教育背景 |
| `ProjectExperience` | 项目经历 |
| `Certificate` | 证书认证 |

### IT 模型（3 张表）

| 模型 | 说明 |
|------|------|
| `ITAsset` | IT 设备资产（编号/类型/品牌/状态/使用人） |
| `ITTicket` | IT 工单（报修/密码重置/软件安装/权限申请） |
| `ITAssetHistory` | 设备流转记录（分配/回收/调拨） |

### 行政模型（6 张表）

| 模型 | 说明 |
|------|------|
| `MeetingRoom` | 会议室（名称/楼层/容量/设备/状态） |
| `RoomBooking` | 会议室预订（30 分钟槽位制，含冲突检测） |
| `OfficeSupply` | 办公用品库存（名称/分类/库存/单位） |
| `SupplyRequest` | 办公用品申领单（审批后自动扣减库存） |
| `Express` | 快递收发记录（单号/类型/状态） |
| `Visitor` | 访客预约（访客信息/来访日期/接待人/状态） |

## 认证与权限

- **认证方式**: JWT Token
- **Token 载荷**: `employee_id`、`roles`、`department_id`

| 角色 | 说明 | 数据范围 |
|------|------|----------|
| **员工** (默认) | 查询/操作自己的数据 | 本人 |
| **主管** (manager) | 查看管辖部门员工数据（不含薪资社保），审批下属申请 | 本部门 |
| **管理者** (admin) | 全公司数据查询（含薪资社保），全公司审批 | 全公司 |
| **人才发展** (talent_dev) | 员工档案、培训、盘点、IDP、分析报表 | 全公司 |
| **IT 管理员** (it_admin) | 全部工单管理、设备分配回收、统计报表 | 全公司 |
| **行政人员** (admin_staff) | 预订管理、用品审批、快递登记、访客管理、统计 | 全公司 |
| **财务人员** (finance) | 报销审核、预算分析、应收应付、开票、费用报表 | 全公司 |
| **法务人员** (legal) | 合同台账、合同审查、到期预警、条款分析、统计报表 | 全公司 |

## HR 助手

### Skills 知识库

| Skill | 描述 | 参考文档 | 计算脚本 | 权限 |
|-------|------|----------|----------|------|
| `leave` | 假期制度 | `references/policy.md` | `calc_annual_leave.py` | 全员 |
| `attendance` | 考勤制度 | `references/policy.md` | `calc_overtime.py` | 全员 |
| `salary` | 薪酬福利 | `references/policy.md` | `calc_tax.py` | 全员 |
| `social-insurance` | 社保公积金 | `references/policy.md` | — | 全员 |
| `onboarding` | 入职流程 | `references/checklist.md` | — | 全员 |
| `resignation` | 离职流程 | `references/process.md` | — | 全员 |
| `reimbursement` | 报销政策 | `references/policy.md` | — | 全员 |
| `training` | 培训制度 | `references/policy.md` | — | 全员 |

### Tools 工具集

#### 员工自助

| 工具 | 文件 | 说明 |
|------|------|------|
| `get_employee_info` | `tools/hr/query.py` | 查询个人基本信息 |
| `get_salary_records` | `tools/hr/query.py` | 查询薪资明细 |
| `get_social_insurance` | `tools/hr/query.py` | 查询社保缴纳 |
| `get_attendance` | `tools/hr/query.py` | 查询考勤记录 |
| `get_leave_balance` | `tools/hr/query.py` | 查询假期余额 |
| `get_leave_requests` | `tools/hr/query.py` | 查询请假记录 |
| `get_overtime_records` | `tools/hr/query.py` | 查询加班记录 |
| `apply_leave` | `tools/hr/action.py` | 发起请假申请 |
| `apply_overtime` | `tools/hr/action.py` | 发起加班登记 |
| `apply_reimbursement` | `tools/hr/action.py` | 发起报销申请 |

#### 主管权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `get_team_members` | `tools/hr/manager_query.py` | 查询团队成员 |
| `get_team_attendance` | `tools/hr/manager_query.py` | 查询团队考勤 |
| `get_team_leave_requests` | `tools/hr/manager_query.py` | 查询团队请假 |
| `get_team_leave_balances` | `tools/hr/manager_query.py` | 查询团队假期余额 |
| `get_team_overtime_records` | `tools/hr/manager_query.py` | 查询团队加班 |
| `get_employee_profile` | `tools/hr/manager_query.py` | 查询员工档案 |
| `approve_leave_request` | `tools/hr/manager_action.py` | 审批请假申请 |
| `approve_overtime_request` | `tools/hr/manager_action.py` | 审批加班申请 |

#### 管理者权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `admin_get_all_employees` | `tools/hr/admin_query.py` | 全员列表 |
| `admin_get_employee_salary` | `tools/hr/admin_query.py` | 任意员工薪资 |
| `admin_get_employee_social_insurance` | `tools/hr/admin_query.py` | 任意员工社保 |
| `admin_get_employee_profile` | `tools/hr/admin_query.py` | 任意员工完整档案 |
| `admin_get_all_leave_requests` | `tools/hr/admin_query.py` | 全公司请假记录 |
| `admin_get_all_attendance` | `tools/hr/admin_query.py` | 全公司考勤记录 |
| `admin_get_all_overtime_records` | `tools/hr/admin_query.py` | 全公司加班记录 |
| `admin_get_department_headcount` | `tools/hr/admin_query.py` | 部门人数统计 |
| `admin_get_attendance_summary` | `tools/hr/admin_query.py` | 考勤汇总报表 |
| `admin_get_salary_summary` | `tools/hr/admin_query.py` | 薪资汇总报表 |
| `admin_get_leave_summary` | `tools/hr/admin_query.py` | 假期汇总报表 |
| `admin_approve_leave_request` | `tools/hr/admin_action.py` | 全公司请假审批 |
| `admin_approve_overtime_request` | `tools/hr/admin_action.py` | 全公司加班审批 |

#### 人才发展权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `td_get_employee_profile` | `tools/hr/talent_dev_query.py` | 员工完整档案 |
| `td_get_employee_training` | `tools/hr/talent_dev_query.py` | 培训记录 |
| `td_get_employee_talent_review` | `tools/hr/talent_dev_query.py` | 人才盘点（九宫格） |
| `td_get_employee_idp` | `tools/hr/talent_dev_query.py` | 个人发展计划 |
| `td_get_employee_performance` | `tools/hr/talent_dev_query.py` | 绩效详情 |
| `td_get_employee_history` | `tools/hr/talent_dev_query.py` | 岗位变动履历 |
| `td_get_employee_attendance` | `tools/hr/talent_dev_query.py` | 考勤记录 |
| `td_get_employee_skills` | `tools/hr/talent_dev_query.py` | 技能标签 |
| `td_get_employee_education` | `tools/hr/talent_dev_query.py` | 教育背景 |
| `td_get_employee_projects` | `tools/hr/talent_dev_query.py` | 项目经历 |
| `td_get_employee_certificates` | `tools/hr/talent_dev_query.py` | 证书认证 |
| `td_training_summary` | `tools/hr/talent_dev_query.py` | 培训完成率统计 |
| `td_nine_grid_distribution` | `tools/hr/talent_dev_query.py` | 九宫格分布 |
| `td_performance_distribution` | `tools/hr/talent_dev_query.py` | 绩效评级分布 |
| `td_turnover_analysis` | `tools/hr/talent_dev_query.py` | 人员流动分析 |
| `td_promotion_stats` | `tools/hr/talent_dev_query.py` | 晋升统计 |
| `td_idp_summary` | `tools/hr/talent_dev_query.py` | IDP 达成率 |

#### 人才发现（talent_dev 权限）

| 工具 | 文件 | 说明 |
|------|------|------|
| `td_discover_hidden_talent` | `tools/hr/discovery.py` | 识别被埋没的高潜人才 |
| `td_assess_flight_risk` | `tools/hr/discovery.py` | 流失风险预警 |
| `td_promotion_readiness` | `tools/hr/discovery.py` | 晋升准备度评估 |
| `td_find_candidates` | `tools/hr/discovery.py` | 岗位适配推荐 |
| `td_talent_portrait` | `tools/hr/discovery.py` | 完整人才画像 |
| `td_team_capability_gap` | `tools/hr/discovery.py` | 团队能力短板分析 |

## IT 运维助手

### Skills 知识库

| Skill | 描述 | 权限 |
|-------|------|------|
| `wifi-vpn` | WiFi/VPN 连接排查指南 | 全员 |
| `printer` | 打印机安装和故障排查 | 全员 |
| `email` | 邮箱配置和常见问题 | 全员 |
| `security` | 信息安全制度和规范 | 全员 |
| `device-policy` | 设备使用规范和借用流程 | 全员 |

### Tools 工具集

#### 员工自助

| 工具 | 文件 | 说明 |
|------|------|------|
| `it_get_my_tickets` | `tools/it/query.py` | 查询我的工单列表 |
| `it_get_ticket_detail` | `tools/it/query.py` | 查询工单详情 |
| `it_get_my_assets` | `tools/it/query.py` | 查询我的设备 |
| `it_create_ticket` | `tools/it/action.py` | 创建 IT 工单 |

#### IT 管理员权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `it_admin_get_tickets` | `tools/it/admin_query.py` | 全部工单查询（多条件筛选） |
| `it_admin_get_assets` | `tools/it/admin_query.py` | 全部设备查询 |
| `it_admin_ticket_stats` | `tools/it/admin_query.py` | 工单统计报表 |
| `it_admin_asset_stats` | `tools/it/admin_query.py` | 设备统计报表 |
| `it_admin_fault_trend` | `tools/it/admin_query.py` | 故障趋势分析 |
| `it_admin_handle_ticket` | `tools/it/admin_action.py` | 处理工单（受理/解决/关闭） |
| `it_admin_assign_asset` | `tools/it/admin_action.py` | 分配设备给员工 |
| `it_admin_reclaim_asset` | `tools/it/admin_action.py` | 回收设备 |

## 行政助手

### Skills 知识库

| Skill | 描述 | 权限 |
|-------|------|------|
| `travel-policy` | 差旅管理制度（交通/住宿/餐费标准、审批流程） | 全员 |
| `office-rules` | 办公管理规范（工位/公共区域/用品领用） | 全员 |
| `meeting-room-rules` | 会议室使用规范（预订/取消/超时规则） | 全员 |

### Tools 工具集

#### 员工自助

| 工具 | 文件 | 说明 |
|------|------|------|
| `adm_get_available_rooms` | `tools/admin/query.py` | 查询可用会议室（支持时间段筛选） |
| `adm_get_my_bookings` | `tools/admin/query.py` | 查询我的预订记录 |
| `adm_get_my_express` | `tools/admin/query.py` | 查询我的快递记录 |
| `adm_get_my_visitors` | `tools/admin/query.py` | 查询我的访客预约 |
| `adm_book_room` | `tools/admin/action.py` | 预订会议室（30 分钟槽位，冲突检测） |
| `adm_cancel_booking` | `tools/admin/action.py` | 取消预订（开始前 30 分钟） |
| `adm_request_supply` | `tools/admin/action.py` | 申领办公用品 |
| `adm_book_visitor` | `tools/admin/action.py` | 预约访客来访 |
| `adm_apply_travel` | `tools/admin/action.py` | 差旅申请（返回 OA 审批链接） |

#### 行政人员权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `adm_admin_get_all_bookings` | `tools/admin/admin_query.py` | 全部预订查询（按会议室/状态/日期） |
| `adm_admin_get_supply_requests` | `tools/admin/admin_query.py` | 全部申领单查询 |
| `adm_admin_get_supply_stock` | `tools/admin/admin_query.py` | 库存查询 |
| `adm_admin_get_all_express` | `tools/admin/admin_query.py` | 全部快递查询 |
| `adm_admin_get_visitors` | `tools/admin/admin_query.py` | 全部访客预约查询 |
| `adm_admin_usage_stats` | `tools/admin/admin_query.py` | 行政综合统计 |
| `adm_admin_release_room` | `tools/admin/admin_action.py` | 设置会议室状态（维护/恢复） |
| `adm_admin_approve_supply` | `tools/admin/admin_action.py` | 审批申领单（通过自动扣库存） |
| `adm_admin_register_express` | `tools/admin/admin_action.py` | 登记快递 |

## 财务助手

### Skills 知识库

| Skill | 描述 | 权限 |
|-------|------|------|
| `reimbursement-policy` | 报销政策（标准/流程/限额/票据要求） | 全员 |
| `budget-rules` | 预算管理制度（编制/调整/超支审批） | 全员 |
| `tax-knowledge` | 个税计算与专项扣除知识 | 全员 |

### Tools 工具集

#### 员工自助

| 工具 | 文件 | 说明 |
|------|------|------|
| `fin_get_my_reimbursements` | `tools/finance/query.py` | 查询我的报销记录 |
| `fin_get_reimbursement_detail` | `tools/finance/query.py` | 查询报销单详情 |
| `fin_get_department_budget` | `tools/finance/query.py` | 查询部门预算概况 |
| `fin_get_my_tax` | `tools/finance/query.py` | 查询个人个税明细（跨域读 HR 薪资） |

#### 主管权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `fin_mgr_get_budget_overview` | `tools/finance/manager_query.py` | 部门预算执行总览 |
| `fin_mgr_get_expense_detail` | `tools/finance/manager_query.py` | 部门费用明细 |
| `fin_mgr_get_budget_alert` | `tools/finance/manager_query.py` | 预算预警（超支/接近上限） |

#### 财务人员权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `fin_admin_get_all_reimbursements` | `tools/finance/admin_query.py` | 全公司报销查询（多条件筛选） |
| `fin_admin_get_expense_summary` | `tools/finance/admin_query.py` | 费用汇总报表 |
| `fin_admin_get_budget_analysis` | `tools/finance/admin_query.py` | 预算分析报表 |
| `fin_admin_get_payables` | `tools/finance/admin_query.py` | 应付账款查询 |
| `fin_admin_get_receivables` | `tools/finance/admin_query.py` | 应收账款查询 |
| `fin_admin_review_reimbursement` | `tools/finance/admin_action.py` | 审核报销单（通过自动扣预算） |
| `fin_admin_process_invoice_request` | `tools/finance/admin_action.py` | 处理开票申请 |

### 数据模型（6 张表）

| 模型 | 说明 |
|------|------|
| `Reimbursement` | 报销单（申请人/部门/金额/状态） |
| `ReimbursementItem` | 报销明细行（费用类型/金额/日期） |
| `Budget` | 部门年度预算（科目/总额/已用/余额） |
| `BudgetUsage` | 预算使用流水（关联报销单/金额） |
| `Payable` | 应付账款（供应商/金额/到期日/状态） |
| `Receivable` | 应收账款（客户/金额/到期日/状态） |

## 法务助手

### Skills 知识库

| Skill | 描述 | 权限 |
|-------|------|------|
| `labor-law` | 劳动法知识（劳动合同法/试用期/解雇保护/经济补偿） | 全员 |
| `contract-knowledge` | 合同知识（签订流程/竞业限制/保密协议/知识产权） | 全员 |
| `compliance` | 合规知识（反腐败/数据隐私/审计配合） | 全员 |

### Tools 工具集

#### 员工自助

| 工具 | 文件 | 说明 |
|------|------|------|
| `leg_get_templates` | `tools/legal/query.py` | 查询合同模板列表（按类型筛选） |
| `leg_get_template_download` | `tools/legal/query.py` | 获取模板下载链接（OA 地址） |
| `leg_get_my_contracts` | `tools/legal/query.py` | 查询我的合同审批进度 |

#### 法务人员权限

| 工具 | 文件 | 说明 |
|------|------|------|
| `leg_admin_get_contracts` | `tools/legal/admin_query.py` | 全公司合同台账（多条件筛选） |
| `leg_admin_get_expiring` | `tools/legal/admin_query.py` | 到期预警（默认 30 天内） |
| `leg_admin_get_stats` | `tools/legal/admin_query.py` | 合同统计报表 |
| `leg_admin_review_contract` | `tools/legal/admin_action.py` | 审查合同（通过/退回） |
| `leg_admin_analyze_contract` | `tools/legal/admin_action.py` | LLM 辅助条款分析（风险识别+建议） |

### 数据模型（3 张表）

| 模型 | 说明 |
|------|------|
| `ContractTemplate` | 合同模板（名称/类型/说明/下载链接） |
| `Contract` | 合同记录（编号/标题/甲乙方/金额/期限/状态/摘要/关键条款） |
| `ContractReview` | 合同审查记录（审查人/动作/意见） |

## 跨域协作

Router Team 支持识别涉及多个部门的跨域场景，依次协调多个子 Agent 并汇总回复：

| 场景 | 调度链路 |
|------|---------|
| 新员工入职 | HR → IT → Admin → Finance |
| 员工离职 | HR → IT → Admin → Finance |
| 出差全流程 | Admin → HR → Finance |

## 模型评估

各角色 Agent 评估用例：

| 角色 | 文件 | 工具数 | 用例数 |
|------|------|--------|--------|
| 普通员工 | `tests/test_evaluation_employee_role.md` | 10 | ~40 |
| 主管 (manager) | `tests/test_evaluation_manager_role.md` | 18 | ~40 |
| 管理者 (admin) | `tests/test_evaluation_admin_role.md` | 23 | ~35 |
| 人才发展 (talent_dev) | `tests/test_evaluation_talent_dev_role.md` | 23 | ~60 |
| 人才发现引擎 | `tests/test_evaluation_talent_discovery.md` | 6 | ~80 |
| IT 运维助手 | `tests/test_evaluation_it_assistant.md` | 12 | 61 |
| 行政助手 | `tests/test_evaluation_admin_assistant.md` | 18 | 51 |
| 财务助手 | `tests/test_evaluation_finance_assistant.md` | 14 | 49 |
| 法务助手 | `tests/test_evaluation_legal_assistant.md` | 8 | 48 |
| 跨域协作 | `tests/test_evaluation_cross_domain.md` | — | 15 |

评估维度：路由识别、功能查询、业务办理、Skills 咨询、权限边界、工具选择歧义、边界异常、跨域协调。

## 异常处理

| 异常类型 | HTTP 状态码 | 业务错误码 | 场景 |
|----------|-------------|------------|------|
| `UnauthorizedException` | 401 | `TOKEN_MISSING` | Token 缺失/过期 |
| `ForbiddenException` | 403 | `FORBIDDEN` | 权限不足 |
| `NotFoundException` | 404 | `NOT_FOUND` | 资源不存在 |
| `ValidationException` | 422 | `VALIDATION_ERROR` | 参数校验失败 |
| `BusinessException` | 400 | `BAD_REQUEST` | 业务逻辑错误 |
| `ExternalServiceException` | 502 | `EXTERNAL_SERVICE_ERROR` | 外部服务调用失败 |
