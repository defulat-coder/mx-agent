"""Unified chat endpoint facade over the AgentOS router team."""

from typing import Any

from fastapi import APIRouter, Request

from app.agents.router_agent import router_team
from app.core.auth import claims_to_session_state, claims_to_user_id, decode_auth_claims
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


async def run_router_chat(req: ChatRequest, claims: dict[str, Any]) -> ChatResponse:
    """Run the router team and normalize AgentOS output to the product API."""
    result = await router_team.arun(
        req.message,
        session_id=req.session_id,
        session_state=claims_to_session_state(claims),
        user_id=claims_to_user_id(claims),
    )
    reply = getattr(result, "content", result)
    session_id = getattr(result, "session_id", req.session_id)
    return ChatResponse(reply=str(reply or ""), action=None, session_id=session_id)


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    claims = decode_auth_claims(request)
    return await run_router_chat(req, claims)
