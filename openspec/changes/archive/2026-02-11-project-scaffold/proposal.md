## Why

搭建喜马智能助手的项目基础框架。项目需要支撑 HR/财务/法务三个子智能体，当前缺少统一的项目骨架、路由分发机制和基础设施层。先建基座，后续各业务 Agent 才能快速接入。

## What Changes

- 初始化 FastAPI 应用骨架（入口、配置、中间件、异常处理）
- 建立 agno Router Agent 作为统一入口，按意图分发到子 Agent
- 搭建数据库基础设施（SQLAlchemy 2.0.46 async ORM + 连接管理）
- 建立 Agent 层鉴权机制（employee_id 注入与强制过滤）
- 定义 /v1/chat 统一对话接口
- 创建 HR/Finance/Legal Agent 占位结构
- 建立统一日志系统（loguru）

## Capabilities

### New Capabilities

- `api-gateway`: FastAPI 应用入口、路由聚合、/v1/chat 接口定义
- `router-agent`: agno Router Agent，意图识别与子 Agent 分发
- `auth`: Agent 层鉴权中间件，员工身份识别与 employee_id 注入
- `database`: SQLAlchemy async ORM 基础设施、连接池、Base Model
- `agent-scaffold`: HR/Finance/Legal Agent 占位骨架与 Skills 加载机制
- `logging`: 基于 loguru 的统一日志系统，替换 stdlib logging，集成 FastAPI/uvicorn 日志

### Modified Capabilities

（无，全新项目）

## Impact

- 新增依赖：fastapi, uvicorn, agno, sqlalchemy, asyncpg, pydantic-settings, loguru
- 建立 app/ 目录结构
- 后续所有业务 Agent 基于此框架开发
