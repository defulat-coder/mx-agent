## 1. HR 提示词修复

- [x] 1.1 更新 `app/agents/hr_agent.py`，补充 talent_dev discovery 工具选择指引
- [x] 1.2 更新 `app/agents/hr_agent.py`，补充人才分析输出结构约束

## 2. IT 提示词修复

- [x] 2.1 更新 `app/agents/it_agent.py`，补充 `it_*` 与 `it_admin_*` 映射说明
- [x] 2.2 更新 `app/agents/it_agent.py`，补充权限失败不重试与替代路径规则

## 3. Router 失败聚合规则修复

- [x] 3.1 更新 `app/agents/router_agent.py`，补充跨域场景失败标注规则
- [x] 3.2 更新 `app/agents/router_agent.py`，补充部分成功场景的汇总输出规则

## 4. 验证与回归

- [x] 4.1 运行静态检查与类型检查，确认提示词修改未引入错误
- [x] 4.2 执行关键场景验证（talent_dev、IT 权限失败、跨域部分失败）并记录结果
