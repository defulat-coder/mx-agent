"""统一错误响应 Schema — 定义 API 错误响应的标准格式。"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """统一错误响应模型。

    Attributes:
        code: 业务错误码
        message: 用户可读的错误描述
        detail: 可选细节信息，DEBUG 模式下可含 traceback
        request_id: 当前请求的唯一标识
        timestamp: ISO 8601 格式时间戳
    """

    code: int = Field(description="业务错误码")
    message: str = Field(description="用户可读的错误描述")
    detail: str | None = Field(default=None, description="错误详情，DEBUG 模式下可含 traceback")
    request_id: str = Field(default="", description="当前请求的唯一标识")
    timestamp: str = Field(default="", description="ISO 8601 格式时间戳")
