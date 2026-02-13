# auth

MODIFIED — 新增 `admin_staff` 角色

## Changes

### CHG-AUTH-ADM-1: Mock 用户追加 admin_staff 角色

`app/tools/hr/utils.py` 的 `_MOCK_EMPLOYEES` 中给郑晓明追加 `admin_staff` 角色。

### CHG-AUTH-ADM-2: generate_token.py 追加 admin_staff

`scripts/generate_token.py` 的 USERS["manager"] roles 列表追加 `admin_staff`。

### CHG-AUTH-ADM-3: utils.py 新增 get_admin_staff_id

`app/tools/admin/utils.py` 参照 `get_it_admin_id`，校验 `admin_staff` 角色。
