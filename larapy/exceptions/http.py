"""HTTP exception classes for Larapy"""

from .base import LarapyException

class HttpException(LarapyException):
    """Base HTTP exception"""
    pass

class NotFoundException(HttpException):
    """404 Not Found exception"""
    status_code = 404
    message = "Not Found"

class ValidationException(HttpException):
    """422 Validation Failed exception"""
    status_code = 422
    message = "Validation Failed"

    def __init__(self, errors=None, message=None):
        super().__init__(message)
        self.errors = errors or {}

class UnauthorizedException(HttpException):
    """401 Unauthorized exception"""
    status_code = 401
    message = "Unauthorized"

class ForbiddenException(HttpException):
    """403 Forbidden exception"""
    status_code = 403
    message = "Forbidden"

class MethodNotAllowedException(HttpException):
    """405 Method Not Allowed exception"""
    status_code = 405
    message = "Method Not Allowed"

class BadRequestException(HttpException):
    """400 Bad Request exception"""
    status_code = 400
    message = "Bad Request"

class TooManyRequestsException(HttpException):
    """429 Too Many Requests exception"""
    status_code = 429
    message = "Too Many Requests"

class InternalServerErrorException(HttpException):
    """500 Internal Server Error exception"""
    status_code = 500
    message = "Internal Server Error"