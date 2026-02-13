# auth

MODIFIED — 新增 `finance` 角色

## Changes

### CHG-AUTH-FIN-1: Mock 用户追加 finance 角色

`app/tools/hr/utils.py` 的 `_MOCK_EMPLOYEES` 中给郑晓明追加 `finance` 角色。

### CHG-AUTH-FIN-2: generate_token.py 追加 finance

`scripts/generate_token.py` 的 USERS["manager"] roles 追加 `finance`。

### CHG-AUTH-FIN-3: utils.py 新增 get_finance_id

`app/tools/finance/utils.py` 校验 `finance` 角色。
