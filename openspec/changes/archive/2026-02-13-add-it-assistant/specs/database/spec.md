## MODIFIED Requirements

### Requirement: 异步数据库连接
系统 SHALL 使用 SQLAlchemy 2.0 async + asyncpg 建立异步数据库连接池。

#### Scenario: 数据库连接池初始化
- **WHEN** 应用启动
- **THEN** 系统创建异步数据库引擎和 session factory

#### Scenario: IT 模型建表
- **WHEN** init_db 执行时
- **THEN** MUST 导入 `app.models.it` 以触发 IT 相关表（it_assets, it_tickets, it_asset_history）的自动创建

#### Scenario: 应用关闭
- **WHEN** 应用关闭
- **THEN** 系统正确释放数据库连接池
