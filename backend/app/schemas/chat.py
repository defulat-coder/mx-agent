"""Chat API schemas."""

from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints


ChatMessage = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)]
SessionID = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]


class ChatRequest(BaseModel):
    """Unified chat request accepted by the product API facade."""

    message: ChatMessage = Field(description="用户消息")
    session_id: SessionID | None = Field(default=None, description="会话 ID，不传则由 AgentOS 生成")


class ChatResponse(BaseModel):
    """Stable product API response for chat clients."""

    reply: str = Field(description="助手回复")
    action: dict[str, Any] | None = Field(default=None, description="结构化动作，当前保留")
    session_id: str | None = Field(default=None, description="会话 ID")
