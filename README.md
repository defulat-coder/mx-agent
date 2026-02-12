# 马喜智能助手 (mx-agent)

基于 FastAPI + Agno 的企业级 AI 智能助手，支持 HR、财务、法务等多领域智能问答与业务办理。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              客户端层                                    │
│                    (Web/移动端/第三方系统)                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API 网关层 (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ RequestID   │  │  日志中间件  │  │ JWT认证     │  │ 异常处理    │    │
│  │ Middleware  │  │             │  │ Middleware  │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AgentOS 运行时 (Agno)                            │
│                         ┌─────────────────┐                             │
│                         │   Router Team   │  ← 智能路由分发              │
│                         │  (智能助手入口)  │                             │
│                         └────────┬────────┘                             │
│                                  │                                      │
│           ┌──────────────────────┼──────────────────────┐              │
│           ▼                      ▼                      ▼              │
│    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐        │
│    │  HR Agent   │       │Finance Agent│       │ Legal Agent │        │
│    │  (已上线)    │       │  (开发中)    │       │  (开发中)    │        │
│    └──────┬──────┘       └─────────────┘       └─────────────┘        │
│           │                                                            │
│    ┌──────┴──────┐                                                     │
│    │             │                                                      │
│    ▼             ▼                                                      │
│ ┌───────┐   ┌─────────┐                                                 │
│ │Skills │   │  Tools  │                                                 │
│ │知识库 │   │ 工具集  │                                                 │
│ └───────┘   └─────────┘                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          数据层                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │   SQLite        │  │  SQLite         │  │   外部系统       │          │
│  │ (业务数据)       │  │ (Agent会话)      │  │  (HR审批系统)    │          │
│  │  - 员工/部门     │  │  - 会话记忆      │  │                │          │
│  │  - 考勤/薪资     │  │  - 追踪数据      │  │                │          │
│  │  - 假期/社保     │  │                │  │                │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **Web 框架** | FastAPI + Uvicorn | RESTful API 服务 |
| **AI 框架** | Agno | 智能体编排与运行 |
| **LLM** | OpenAI API (GLM-4) | 大语言模型调用 |
| **ORM** | SQLAlchemy + aiosqlite | 异步数据库操作 |
| **配置** | Pydantic Settings | 环境变量管理 |
| **日志** | Loguru | 结构化日志 |
| **认证** | PyJWT | JWT Token 认证 |
| **依赖管理** | uv | Python 包管理 |

## 项目结构

```
app/
├── main.py              # FastAPI + AgentOS 入口
├── config.py            # 环境变量配置
├── agents/              # 智能体定义
│   ├── router_agent.py  # 路由智能体 (Team)
│   ├── hr_agent.py      # HR 助手
│   ├── finance_agent.py # 财务助手 (开发中)
│   └── legal_agent.py   # 法务助手 (开发中)
├── api/v1/              # REST API 路由
├── core/                # 基础设施
│   ├── database.py      # 数据库连接
│   ├── exceptions.py    # 异常处理
│   ├── error_codes.py   # 错误码定义
│   ├── middleware.py    # 中间件
│   ├── logging.py       # 日志配置
│   ├── llm.py           # LLM 配置
│   └── context.py       # 请求上下文
├── models/              # SQLAlchemy ORM 模型
│   └── hr/              # HR 领域模型
├── schemas/             # Pydantic 请求/响应 Schema
├── services/            # 业务逻辑层
├── skills/              # Agent Skills (制度知识库)
│   └── hr/              # HR 领域技能
└── tools/               # Agent Tools (数据查询/业务办理)
    └── hr/              # HR 领域工具
```

## 快速启动

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env  # 修改 .env 中的配置

# 启动服务
uv run python main.py
```

服务默认运行在 `http://localhost:8000`。

## 数据模型

| 模型 | 说明 |
|------|------|
| `Employee` | 员工基本信息 |
| `Department` | 部门信息（树形结构） |
| `LeaveBalance` | 假期余额 |
| `LeaveRequest` | 请假申请记录 |
| `SalaryRecord` | 月度薪资明细 |
| `SocialInsurance` | 社保公积金缴纳记录 |
| `Attendance` | 考勤记录 |
| `Overtime` | 加班记录 |
| `PerformanceReview` | 绩效考评 |
| `EmploymentHistory` | 在职履历 |

## HR 助手功能

### 功能矩阵

| 功能类别 | 功能项 | 实现方式 | 权限 |
|----------|--------|----------|------|
| **制度咨询** | 假期制度 | `skills/hr/leave/` | 全员 |
| | 考勤制度 | `skills/hr/attendance/` | 全员 |
| | 薪酬福利 | `skills/hr/salary/` | 全员 |
| | 社保公积金 | `skills/hr/social-insurance/` | 全员 |
| | 入职流程 | `skills/hr/onboarding/` | 全员 |
| | 离职流程 | `skills/hr/resignation/` | 全员 |
| | 报销政策 | `skills/hr/reimbursement/` | 全员 |
| | 培训制度 | `skills/hr/training/` | 全员 |
| **数据查询** | 个人信息 | `get_employee_info` | 本人 |
| | 薪资明细 | `get_salary_records` | 本人 |
| | 社保缴纳 | `get_social_insurance` | 本人 |
| | 考勤记录 | `get_attendance` | 本人 |
| | 假期余额 | `get_leave_balance` | 本人 |
| | 请假记录 | `get_leave_requests` | 本人 |
| | 加班记录 | `get_overtime_records` | 本人 |
| **业务办理** | 请假申请 | `apply_leave` | 本人 |
| | 加班登记 | `apply_overtime` | 本人 |
| | 报销申请 | `apply_reimbursement` | 本人 |
| **主管权限** | 团队列表 | `get_team_members` | 主管 |
| | 团队考勤 | `get_team_attendance` | 主管 |
| | 团队请假 | `get_team_leave_requests` | 主管 |
| | 团队假期余额 | `get_team_leave_balances` | 主管 |
| | 团队加班 | `get_team_overtime_records` | 主管 |
| | 员工档案 | `get_employee_profile` | 主管 |
| | 审批请假 | `approve_leave_request` | 主管 |
| | 审批加班 | `approve_overtime_request` | 主管 |

### Skills 知识库

| Skill | 描述 | 参考文档 | 计算脚本 |
|-------|------|----------|----------|
| `leave` | 假期制度咨询 | `references/policy.md` | `calc_annual_leave.py` |
| `attendance` | 考勤制度咨询 | `references/policy.md` | `calc_overtime.py` |
| `salary` | 薪酬福利咨询 | `references/policy.md` | `calc_tax.py` |
| `social-insurance` | 社保公积金咨询 | `references/policy.md` | - |
| `onboarding` | 入职流程咨询 | `references/checklist.md` | - |
| `resignation` | 离职流程咨询 | `references/process.md` | - |
| `reimbursement` | 报销政策咨询 | `references/policy.md` | - |
| `training` | 培训制度咨询 | `references/policy.md` | - |

### Tools 工具集

**员工查询工具** (`tools/hr/query.py`)：
- `get_employee_info` — 查询员工基本信息
- `get_salary_records` — 查询薪资明细
- `get_social_insurance` — 查询社保缴纳
- `get_attendance` — 查询考勤记录
- `get_leave_balance` — 查询假期余额
- `get_leave_requests` — 查询请假记录
- `get_overtime_records` — 查询加班记录

**员工办理工具** (`tools/hr/action.py`)：
- `apply_leave` — 发起请假申请
- `apply_overtime` — 发起加班登记
- `apply_reimbursement` — 发起报销申请

**主管查询工具** (`tools/hr/manager_query.py`)：
- `get_team_members` — 查询团队成员
- `get_team_attendance` — 查询团队考勤
- `get_team_leave_requests` — 查询团队请假
- `get_team_leave_balances` — 查询团队假期余额
- `get_team_overtime_records` — 查询团队加班
- `get_employee_profile` — 查询员工档案

**主管审批工具** (`tools/hr/manager_action.py`)：
- `approve_leave_request` — 审批请假申请
- `approve_overtime_request` — 审批加班申请

## 认证与权限

- **认证方式**: JWT Token
- **Token 载荷**: `employee_id`, `roles`, `department_id`
- **权限控制**:
  - 普通员工只能查询/操作自己的数据
  - 主管可查看管辖部门及子部门的员工数据
  - 主管不可查看下属薪资和社保数据

## 异常处理

| 异常类型 | HTTP 状态码 | 业务错误码 | 场景 |
|----------|-------------|------------|------|
| `UnauthorizedException` | 401 | `TOKEN_MISSING` | Token 缺失/过期 |
| `ForbiddenException` | 403 | `FORBIDDEN` | 权限不足 |
| `NotFoundException` | 404 | `NOT_FOUND` | 资源不存在 |
| `ValidationException` | 422 | `VALIDATION_ERROR` | 参数校验失败 |
| `BusinessException` | 400 | `BAD_REQUEST` | 业务逻辑错误 |
| `ExternalServiceException` | 502 | `EXTERNAL_SERVICE_ERROR` | 外部服务调用失败 |
