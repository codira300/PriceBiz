from typing import Optional
import logging

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.services.auth import (
    InvalidTokenError,
    decode_access_token,
)

from app.database.users import get_user_by_id

from app.monitoring.metrics import (
    AUTH_FAILURES_TOTAL,
)


logger = logging.getLogger("pricebiz")


security = HTTPBearer(
    auto_error=False,
)


async def get_current_user(
    request: Request,
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(security),
):

    if credentials is None:

        AUTH_FAILURES_TOTAL.labels(
            method="access_token",
            reason="missing_credentials",
        ).inc()

        raise HTTPException(
            status_code=401,
            detail="Authentication credentials are required",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if credentials.scheme.lower() != "bearer":

        AUTH_FAILURES_TOTAL.labels(
            method="access_token",
            reason="invalid_scheme",
        ).inc()

        raise HTTPException(
            status_code=401,
            detail="Authentication scheme must be Bearer",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token = credentials.credentials.strip()

    if not token:

        AUTH_FAILURES_TOTAL.labels(
            method="access_token",
            reason="empty_token",
        ).inc()

        raise HTTPException(
            status_code=401,
            detail="Authentication token cannot be empty",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:
        payload = decode_access_token(
            token
        )

    except InvalidTokenError as exc:

        AUTH_FAILURES_TOTAL.labels(
            method="access_token",
            reason="invalid_token",
        ).inc()

        logger.warning(
            "Access token authentication failed"
        )

        raise HTTPException(
            status_code=401,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload["sub"]

    user = await get_user_by_id(
        user_id
    )

    if not user:

        AUTH_FAILURES_TOTAL.labels(
            method="access_token",
            reason="user_not_found",
        ).inc()

        logger.warning(
            "Access token authentication failed | "
            "reason=user_not_found"
        )

        raise HTTPException(
            status_code=401,
            detail="Authenticated user no longer exists",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    request.state.user = user
    request.state.user_id = str(
        user["_id"]
    )

    return user