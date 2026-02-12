## ADDED Requirements

### Requirement: 对话历史持久化
系统 SHALL 使用 agno SqliteDb 将对话历史按 user_id + session_id 持久化到独立 SQLite 文件。

#### Scenario: 同会话多轮对话
- **WHEN** 用户在同一 session_id 下发送多条消息
- **THEN** Agent 能访问该会话的历史消息，实现多轮对话上下文

#### Scenario: 不同会话隔离
- **WHEN** 用户使用不同 session_id 发送消息
- **THEN** 各会话的对话历史互不影响

#### Scenario: 不同用户隔离
- **WHEN** 不同 user_id 的用户使用相同 session_id
- **THEN** 各用户的对话历史互不影响

### Requirement: session_id 管理
系统 SHALL 支持前端传入 session_id 续接对话，未传入时自动生成新 session_id。

#### Scenario: 前端传入 session_id
- **WHEN** ChatRequest 携带 session_id
- **THEN** 使用该 session_id 续接已有对话，ChatResponse 返回相同 session_id

#### Scenario: 前端未传 session_id
- **WHEN** ChatRequest 未携带 session_id
- **THEN** 后端生成新 UUID 作为 session_id，ChatResponse 返回该 session_id

### Requirement: 会话存储独立
Agent 会话数据 SHALL 存储在独立 SQLite 文件（data/agent_sessions.db），与业务数据库分离。

#### Scenario: 业务 DB 重建不影响对话
- **WHEN** 业务数据库被 seed 脚本重建
- **THEN** 对话历史不受影响
