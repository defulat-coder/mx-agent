"""生成测试用 JWT Token — 包含 employee_id、roles、department_id 等 claims"""

import sys
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "change-me-in-production"
ALGORITHM = "HS256"

# 预设测试用户
USERS = {
    "employee": {
        "sub": "1",
        "employee_id": 1,
        "employee_no": "MX0001",
        "name": "张三",
        "roles": ["employee"],
        "department_id": None,
    },
    "manager": {
        "sub": "9",
        "employee_id": 9,
        "employee_no": "MX0009",
        "name": "郑晓明",
        "roles": ["employee", "manager", "admin", "talent_dev", "it_admin", "admin_staff"],
        "department_id": 2,
    },
}


def generate(user_type: str = "employee", days: int = 7) -> str:
    """生成指定角色的 JWT token。"""
    payload = USERS.get(user_type)
    if not payload:
        print(f"未知用户类型: {user_type}，可选: {', '.join(USERS.keys())}")
        sys.exit(1)

    payload = {
        **payload,
        "exp": datetime.now(timezone.utc) + timedelta(days=days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


if __name__ == "__main__":
    user_type = sys.argv[1] if len(sys.argv) > 1 else "employee"
    token = generate(user_type)
    print(f"User: {user_type}")
    print(f"Token: {token}")
