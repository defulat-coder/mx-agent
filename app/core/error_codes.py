"""业务错误码常量 — 按 {HTTP状态码前3位}{序号2位} 编码。"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """业务错误码，按模块编码。

    编码规则: {HTTP状态码前3位}{序号2位}
    """

    # 400xx 通用客户端错误
    BAD_REQUEST = 40001

    # 401xx 认证错误
    TOKEN_MISSING = 40101
    TOKEN_EXPIRED = 40102
    TOKEN_INVALID = 40103

    # 403xx 权限错误
    FORBIDDEN = 40301

    # 404xx 资源不存在
    NOT_FOUND = 40401

    # 422xx 参数校验
    VALIDATION_ERROR = 42201

    # 500xx 服务内部错误
    INTERNAL_ERROR = 50001

    # 502xx 外部服务错误
    EXTERNAL_SERVICE_ERROR = 50201
