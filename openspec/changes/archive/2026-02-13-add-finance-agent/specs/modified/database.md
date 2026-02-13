# database

MODIFIED — init_db 导入财务模型触发建表

## Changes

### CHG-DB-FIN-1: 导入财务模型

`app/core/database.py` 的 `init_db` 函数中追加 `import app.models.finance  # noqa: F401`。
