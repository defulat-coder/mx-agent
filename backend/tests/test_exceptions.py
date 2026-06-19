"""异常处理测试"""

from app.core.error_codes import ErrorCode
from app.core.exceptions import (
    AppException,
    BusinessException,
    ExternalServiceException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


def test_app_exception_defaults():
    exc = AppException()
    assert exc.status_code == 400
    assert exc.code == ErrorCode.BAD_REQUEST
    assert exc.message == "请求错误"


def test_unauthorized_exception():
    exc = UnauthorizedException()
    assert exc.status_code == 401
    assert exc.code == ErrorCode.TOKEN_MISSING


def test_not_found_exception():
    exc = NotFoundException()
    assert exc.status_code == 404
    assert exc.code == ErrorCode.NOT_FOUND


def test_forbidden_exception():
    exc = ForbiddenException()
    assert exc.status_code == 403
    assert exc.code == ErrorCode.FORBIDDEN


def test_validation_exception():
    exc = ValidationException()
    assert exc.status_code == 422
    assert exc.code == ErrorCode.VALIDATION_ERROR


def test_business_exception():
    exc = BusinessException()
    assert exc.status_code == 400
    assert exc.code == ErrorCode.BAD_REQUEST


def test_external_service_exception():
    exc = ExternalServiceException()
    assert exc.status_code == 502
    assert exc.code == ErrorCode.EXTERNAL_SERVICE_ERROR


def test_custom_code_and_message():
    exc = UnauthorizedException(code=ErrorCode.TOKEN_EXPIRED, message="token 已过期")
    assert exc.code == ErrorCode.TOKEN_EXPIRED
    assert exc.message == "token 已过期"
