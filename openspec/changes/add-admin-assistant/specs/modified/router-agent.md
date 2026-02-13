# router-agent

MODIFIED — 追加 Admin Agent 成员和路由规则

## Changes

### CHG-ROUTER-ADM-1: 导入 admin_agent

`app/agents/router_agent.py` 追加 `from app.agents.admin_agent import admin_agent`。

### CHG-ROUTER-ADM-2: members 追加

`router_team.members` 追加 `admin_agent`。

### CHG-ROUTER-ADM-3: instructions 增加路由规则

追加："行政相关问题（会议室预订、办公用品、快递收发、访客预约、差旅申请等）→ Admin Assistant"
