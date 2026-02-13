## MODIFIED Requirements

### Requirement: 异步数据库连接
系统 SHALL 使用 SQLAlchemy 2.0 async + aiosqlite 建立异步数据库连接。

#### Scenario: 数据库连接初始化
- **WHEN** 应用启动
- **THEN** 系统创建异步 SQLite 引擎和 session factory，并执行 `PRAGMA foreign_keys = ON`

#### Scenario: 应用启动自动建表
- **WHEN** 应用启动
- **THEN** 系统通过 metadata.create_all 自动创建所有 ORM 表（如不存在）

#### Scenario: 应用关闭
- **WHEN** 应用关闭
- **THEN** 系统正确释放数据库连接

### Requirement: 数据库配置
数据库连接信息 SHALL 通过环境变量配置，默认使用 SQLite 本地文件。

#### Scenario: 配置读取
- **WHEN** 应用启动
- **THEN** 从 `DATABASE_URL` 环境变量读取连接字符串，默认为 `sqlite+aiosqlite:///data/xm_agent.db`
