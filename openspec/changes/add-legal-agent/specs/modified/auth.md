# auth

MODIFIED — 新增 `legal` 角色

## Changes

### CHG-AUTH-LEG-1: Mock 用户追加 legal 角色

`app/tools/hr/utils.py` 的 `_MOCK_EMPLOYEES` 中给郑晓明追加 `legal` 角色。

### CHG-AUTH-LEG-2: generate_token.py 追加 legal

`scripts/generate_token.py` 的 USERS["manager"] roles 追加 `legal`。

### CHG-AUTH-LEG-3: utils.py 新增 get_legal_id

`app/tools/legal/utils.py` 校验 `legal` 角色，返回 employee_id 或权限不足提示。
