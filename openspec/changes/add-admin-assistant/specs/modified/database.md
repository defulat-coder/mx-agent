# database

MODIFIED — init_db 导入行政模型触发建表

## Changes

### CHG-DB-ADM-1: 导入行政模型

`app/core/database.py` 的 `init_db` 函数中追加 `import app.models.admin  # noqa: F401`。
