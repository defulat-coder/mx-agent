## ADDED Requirements

### Requirement: IT 管理员角色校验
系统 SHALL 在 `app/tools/it/utils.py` 提供 `get_it_admin_id` 函数，校验当前用户是否具备 `it_admin` 角色。

#### Scenario: 具备 it_admin 角色
- **WHEN** session_state.roles 包含 "it_admin"
- **THEN** 返回 employee_id

#### Scenario: 不具备 it_admin 角色
- **WHEN** session_state.roles 不包含 "it_admin"
- **THEN** 抛出 ValueError("该功能仅限 IT 管理员使用")

### Requirement: Mock 用户扩展
系统 SHALL 在 mock 用户数据中包含 `it_admin` 角色。

#### Scenario: 郑晓明默认角色
- **WHEN** 无 JWT 登录态使用系统
- **THEN** 默认模拟用户郑晓明的 roles MUST 包含 "it_admin"

#### Scenario: 生成 token 脚本
- **WHEN** 运行 scripts/generate_token.py 生成郑晓明的 token
- **THEN** JWT claims 的 roles MUST 包含 "it_admin"
