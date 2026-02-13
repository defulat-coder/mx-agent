## ADDED Requirements

### Requirement: 异步数据库连接
系统 SHALL 使用 SQLAlchemy 2.0 async + asyncpg 建立异步数据库连接池。

#### Scenario: 数据库连接池初始化
- **WHEN** 应用启动
- **THEN** 系统创建异步数据库引擎和 session factory

#### Scenario: 应用关闭
- **WHEN** 应用关闭
- **THEN** 系统正确释放数据库连接池

### Requirement: ORM Base Model
系统 SHALL 提供 SQLAlchemy declarative base 和通用 Base Model，包含 id、created_at、updated_at 公共字段。

#### Scenario: 模型定义
- **WHEN** 开发者创建新的 ORM 模型
- **THEN** 继承 Base Model 即自动获得 id (PK)、created_at、updated_at 字段

### Requirement: Session 依赖注入
系统 SHALL 通过 FastAPI Depends 提供异步 DB session，确保请求结束后自动关闭。

#### Scenario: 请求级 session
- **WHEN** endpoint 或 service 需要数据库操作
- **THEN** 通过 `Depends(get_db)` 获取 async session，请求结束后自动 commit/rollback 并关闭

### Requirement: 数据库配置
数据库连接信息 SHALL 通过环境变量配置，支持 .env 文件。

#### Scenario: 配置读取
- **WHEN** 应用启动
- **THEN** 从 `DATABASE_URL` 环境变量读取数据库连接字符串

### Requirement: 模型导入与建表
`init_db` 函数 SHALL 导入所有业务模型模块以触发 ORM 表创建。

#### Scenario: 财务模型建表
- **WHEN** 应用启动调用 `init_db`
- **THEN** `import app.models.finance` 确保财务相关表自动创建
