from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.services.users import (
    UserServiceError,
    InvalidUserError,
    UserNotFoundError,
    DuplicateUserError,
)

logger = logging.getLogger("pricebiz")

def _error_response(
    status_code: int,
    code: str,
    message: str,
    request: Request,
    details=None,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    error = {
        "code": code,
        "message": message,
        "request_id": request_id,
    }

    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
        },
        headers={
            "X-Request-ID": request_id
        } if request_id else None,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return _error_response(
        status_code=exc.status_code,
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        request=request,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    details = []

    for error in exc.errors():
        location = [
            str(item)
            for item in error["loc"]
            if item != "body"
        ]

        details.append(
            {
                "field": ".".join(location),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return _error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        request=request,
        details=details,
    )


async def user_service_exception_handler(
    request: Request,
    exc: UserServiceError,
):
    if isinstance(exc, InvalidUserError):
        status_code = 400
        code = "INVALID_USER"

    elif isinstance(exc, UserNotFoundError):
        status_code = 404
        code = "USER_NOT_FOUND"

    elif isinstance(exc, DuplicateUserError):
        status_code = 409
        code = "DUPLICATE_USER"

    else:
        status_code = 400
        code = "USER_SERVICE_ERROR"

    return _error_response(
        status_code=status_code,
        code=code,
        message=str(exc),
        request=request,
    )


async def value_error_handler(
    request: Request,
    exc: ValueError,
):
    return _error_response(
        status_code=400,
        code="INVALID_VALUE",
        message=str(exc),
        request=request,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    logger.exception(
        "Unhandled application exception | "
        "request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    return _error_response(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        request=request,
    )

def register_exception_handlers(app):
    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        UserServiceError,
        user_service_exception_handler,
    )

    app.add_exception_handler(
        ValueError,
        value_error_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )