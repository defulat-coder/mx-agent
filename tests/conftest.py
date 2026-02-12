import jwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


def make_token(
    employee_id: int = 1,
    employee_no: str = "XM0001",
    name: str = "张三",
    secret: str = settings.AUTH_SECRET,
    expired: bool = False,
) -> str:
    import time

    payload = {
        "employee_id": employee_id,
        "employee_no": employee_no,
        "name": name,
    }
    if expired:
        payload["exp"] = int(time.time()) - 3600
    else:
        payload["exp"] = int(time.time()) + 3600
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def valid_token() -> str:
    return make_token()


@pytest.fixture
def expired_token() -> str:
    return make_token(expired=True)


@pytest.fixture
def auth_headers(valid_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {valid_token}"}


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
