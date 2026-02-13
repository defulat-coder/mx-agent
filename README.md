# 马喜智能助手 (mx-agent)

基于 FastAPI + Agno 的企业级 AI 智能助手，支持 HR、财务、法务等多领域智能问答与业务办理。

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
│                      │  Router Team    │ ← 智能路由分发            │
│                      │  (智能助手入口)   │                          │
│                      └───────┬─────────┘                          │
│              ┌───────────────┼───────────────┐                    │
│              ▼               ▼               ▼                    │
│       ┌───────────┐  ┌────────────┐  ┌───────────┐               │
│       │ HR Agent  │  │ Finance    │  │ Legal     │               │
│       │ (已上线)   │  │ Agent      │  │ Agent     │               │
│       └─────┬─────┘  │ (开发中)    │  │ (开发中)   │               │
│             │        └────────────┘  └───────────┘               │
│       ┌─────┴─────┐                                               │
│       ▼           ▼                                               │
│   ┌────────┐ ┌─────────┐                                          │
│   │ Skills │ │  Tools  │                                          │
│   │ 知识库  │ │  工具集  │                                          │
│   └────────┘ └─────────┘                                          │
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
│   ├── finance_agent.py     #   财务助手 (开发中)
│   └── legal_agent.py       #   法务助手 (开发中)
├── api/v1/                  # REST API 路由
├── core/                    # 基础设施
│   ├── database.py          #   数据库连接
│   ├── llm.py               #   LLM 配置
│   ├── middleware.py         #   中间件 (RequestID / 日志)
│   ├── exceptions.py        #   异常处理
│   ├── error_codes.py       #   错误码定义
│   ├── logging.py           #   日志配置
│   └── context.py           #   请求上下文
├── models/hr/               # SQLAlchemy ORM 模型
├── schemas/                 # Pydantic 请求/响应 Schema
├── services/                # 业务逻辑层
├── skills/hr/               # Agent Skills (制度知识库)
└── tools/hr/                # Agent Tools (数据查询/业务办理)
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

## 认证与权限

- **认证方式**: JWT Token
- **Token 载荷**: `employee_id`、`roles`、`department_id`

| 角色 | 说明 | 数据范围 |
|------|------|----------|
| **员工** (默认) | 查询/操作自己的数据 | 本人 |
| **主管** (manager) | 查看管辖部门员工数据（不含薪资社保），审批下属申请 | 本部门 |
| **管理者** (admin) | 全公司数据查询（含薪资社保），全公司审批 | 全公司 |
| **人才发展** (talent_dev) | 员工档案、培训、盘点、IDP、分析报表 | 全公司 |

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
| `td_training_summary` | `tools/hr/talent_dev_query.py` | 培训完成率统计 |
| `td_nine_grid_distribution` | `tools/hr/talent_dev_query.py` | 九宫格分布 |
| `td_performance_distribution` | `tools/hr/talent_dev_query.py` | 绩效评级分布 |
| `td_turnover_analysis` | `tools/hr/talent_dev_query.py` | 人员流动分析 |
| `td_promotion_stats` | `tools/hr/talent_dev_query.py` | 晋升统计 |
| `td_idp_summary` | `tools/hr/talent_dev_query.py` | IDP 达成率 |

## 异常处理

| 异常类型 | HTTP 状态码 | 业务错误码 | 场景 |
|----------|-------------|------------|------|
| `UnauthorizedException` | 401 | `TOKEN_MISSING` | Token 缺失/过期 |
| `ForbiddenException` | 403 | `FORBIDDEN` | 权限不足 |
| `NotFoundException` | 404 | `NOT_FOUND` | 资源不存在 |
| `ValidationException` | 422 | `VALIDATION_ERROR` | 参数校验失败 |
| `BusinessException` | 400 | `BAD_REQUEST` | 业务逻辑错误 |
| `ExternalServiceException` | 502 | `EXTERNAL_SERVICE_ERROR` | 外部服务调用失败 |
