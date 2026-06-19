"""Unified chat endpoint facade over the AgentOS router team."""

from typing import Any

import jwt
from fastapi import APIRouter, Request

from app.agents.router_agent import router_team
from app.config import settings
from app.core.error_codes import ErrorCode
from app.core.exceptions import UnauthorizedException
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _extract_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if not authorization:
        raise UnauthorizedException(code=ErrorCode.TOKEN_MISSING, message="缺少 token")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 格式无效")
    return token.strip()


def _decode_auth_claims(request: Request) -> dict[str, Any]:
    token = _extract_bearer_token(request)
    try:
        claims = jwt.decode(token, settings.AUTH_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException(code=ErrorCode.TOKEN_EXPIRED, message="token 已过期") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 无效") from exc

    if "employee_id" not in claims:
        raise UnauthorizedException(code=ErrorCode.TOKEN_INVALID, message="token 缺少 employee_id")

    return claims


async def run_router_chat(req: ChatRequest, claims: dict[str, Any]) -> ChatResponse:
    """Run the router team and normalize AgentOS output to the product API."""
    employee_id = claims["employee_id"]
    session_state = {
        "employee_id": employee_id,
        "roles": claims.get("roles", []),
        "department_id": claims.get("department_id"),
    }
    result = await router_team.arun(
        req.message,
        session_id=req.session_id,
        session_state=session_state,
        user_id=str(employee_id),
    )
    reply = getattr(result, "content", result)
    session_id = getattr(result, "session_id", req.session_id)
    return ChatResponse(reply=str(reply or ""), action=None, session_id=session_id)


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    claims = _decode_auth_claims(request)
    return await run_router_chat(req, claims)
