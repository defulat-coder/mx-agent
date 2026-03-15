## 1. HR Agent 动态 Tools

- [x] 1.1 在 `app/agents/hr_agent.py` 中添加 `get_hr_tools(run_context)` 工厂函数
- [x] 1.2 修改 `hr_agent` 的 `tools` 参数从静态列表改为 `get_hr_tools`
- [x] 1.3 简化 HR Agent instructions，移除权限说明段落

## 2. IT Agent 动态 Tools

- [x] 2.1 在 `app/agents/it_agent.py` 中添加 `get_it_tools(run_context)` 工厂函数
- [x] 2.2 修改 `it_agent` 的 `tools` 参数从静态列表改为 `get_it_tools`
- [x] 2.3 简化 IT Agent instructions，移除权限说明段落

## 3. Admin Agent 动态 Tools

- [x] 3.1 在 `app/agents/admin_agent.py` 中添加 `get_admin_tools(run_context)` 工厂函数
- [x] 3.2 修改 `admin_agent` 的 `tools` 参数从静态列表改为 `get_admin_tools`
- [x] 3.3 简化 Admin Agent instructions，移除权限说明段落

## 4. Finance Agent 动态 Tools

- [x] 4.1 在 `app/agents/finance_agent.py` 中添加 `get_finance_tools(run_context)` 工厂函数
- [x] 4.2 修改 `finance_agent` 的 `tools` 参数从静态列表改为 `get_finance_tools`
- [x] 4.3 简化 Finance Agent instructions，移除权限说明段落

## 5. Legal Agent 动态 Tools

- [x] 5.1 在 `app/agents/legal_agent.py` 中添加 `get_legal_tools(run_context)` 工厂函数
- [x] 5.2 修改 `legal_agent` 的 `tools` 参数从静态列表改为 `get_legal_tools`
- [x] 5.3 简化 Legal Agent instructions，移除权限说明段落

## 6. 权限校验函数清理

- [x] 6.1 移除 `app/tools/hr/utils.py` 中 `get_manager_info` 的角色校验逻辑，仅保留 dept_id 提取
- [x] 6.2 移除 `app/tools/hr/utils.py` 中 `get_admin_id` 函数（或简化为仅返回 employee_id）
- [x] 6.3 移除 `app/tools/hr/utils.py` 中 `get_talent_dev_id` 函数

## 7. 验证测试

- [x] 7.1 启动应用验证 Agent 正常初始化
- [x] 7.2 测试普通员工请求，确认只能看到基础 tools
- [x] 7.3 测试主管/管理员请求，确认能看到对应权限的 tools
