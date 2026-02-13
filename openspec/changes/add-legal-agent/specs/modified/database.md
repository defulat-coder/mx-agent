# database

MODIFIED — init_db 导入法务模型触发建表

## Changes

### CHG-DB-LEG-1: 导入法务模型

`app/core/database.py` 的 `init_db` 函数中追加 `import app.models.legal  # noqa: F401`。
