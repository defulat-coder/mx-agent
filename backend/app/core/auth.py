"""Authentication helpers shared by product API facades and AgentOS setup."""

from typing import Any

import jwt
from fastapi import Request

from app.config import settings
from app.core.error_codes import ErrorCode
from app.core.exceptions import UnauthorizedException

SESSION_STATE_CLAIMS = ("employee_id", "roles", "department_id")


def extract_bearer_token(request: Request) -> str:
    """Extract a bearer token from the Authorization header."""
    authorization = request.headers.get("Authorization", "")
    if not authorization:
        raise UnauthorizedException(code=ErrorCode.TOKEN_MISSING, message="缺少 token")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 格式无效")
    return token.strip()


def decode_auth_claims(request: Request) -> dict[str, Any]:
    """Decode JWT claims and map JWT failures to project error codes."""
    token = extract_bearer_token(request)
    try:
        claims = jwt.decode(token, settings.AUTH_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException(code=ErrorCode.TOKEN_EXPIRED, message="token 已过期") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 无效") from exc

    if "employee_id" not in claims:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 缺少 employee_id")

    return claims


def claims_to_session_state(claims: dict[str, Any]) -> dict[str, Any]:
    """Build the AgentOS session_state used by agent tools."""
    return {
        "employee_id": claims["employee_id"],
        "roles": claims.get("roles", []),
        "department_id": claims.get("department_id"),
    }


def claims_to_user_id(claims: dict[str, Any]) -> str:
    """Return the AgentOS user_id for a decoded token."""
    return str(claims["employee_id"])
