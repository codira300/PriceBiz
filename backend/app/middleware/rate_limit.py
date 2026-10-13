import time
from collections import deque
from dataclasses import dataclass
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse

import logging

from app.monitoring.metrics import (
    RATE_LIMIT_EXCEEDED_TOTAL,
)

logger = logging.getLogger("pricebiz")

@dataclass(frozen=True)
class RateLimitRule:
    requests: int
    window_seconds: int


DEFAULT_RULE = RateLimitRule(
    requests=300,
    window_seconds=60,
)

AUTH_RULE = RateLimitRule(
    requests=20,
    window_seconds=60,
)

UPLOAD_RULE = RateLimitRule(
    requests=20,
    window_seconds=60,
)


class RateLimiter:
    def __init__(
        self,
        max_clients: int = 10_000,
    ):
        self.max_clients = max_clients

        self._requests: dict[
            str,
            deque[float],
        ] = {}

        self._lock = Lock()

    def is_allowed(
        self,
        client_key: str,
        rule: RateLimitRule,
    ) -> tuple[bool, int]:
        now = time.monotonic()
        window_start = now - rule.window_seconds

        with self._lock:
            timestamps = self._requests.setdefault(
                client_key,
                deque(),
            )

            while (
                timestamps
                and timestamps[0] <= window_start
            ):
                timestamps.popleft()

            if len(timestamps) >= rule.requests:
                retry_after = max(
                    1,
                    int(
                        timestamps[0]
                        + rule.window_seconds
                        - now
                    ),
                )

                return False, retry_after

            timestamps.append(now)

            return True, 0

    def cleanup(self):
        now = time.monotonic()

        with self._lock:
            expired_clients = []

            for client_key, timestamps in self._requests.items():
                while (
                    timestamps
                    and timestamps[0]
                    <= now - DEFAULT_RULE.window_seconds
                ):
                    timestamps.popleft()

                if not timestamps:
                    expired_clients.append(client_key)

            for client_key in expired_clients:
                self._requests.pop(
                    client_key,
                    None,
                )

            if len(self._requests) <= self.max_clients:
                return

            clients = sorted(
                self._requests.items(),
                key=lambda item: (
                    item[1][-1]
                    if item[1]
                    else 0
                ),
            )

            excess = (
                len(self._requests)
                - self.max_clients
            )

            for client_key, _ in clients[:excess]:
                self._requests.pop(
                    client_key,
                    None,
                )


rate_limiter = RateLimiter()


def _get_client_key(
    request: Request,
) -> str:
    if request.client is None:
        return "unknown"

    return request.client.host


def _get_rule(
    request: Request,
) -> RateLimitRule:
    path = request.url.path.lower()

    if path.startswith("/auth"):
        return AUTH_RULE

    if path.startswith("/uploads"):
        return UPLOAD_RULE

    return DEFAULT_RULE


def _rate_limit_response(
    request: Request,
    retry_after: int,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    response = JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    "Too many requests. "
                    "Please try again later."
                ),
                "request_id": request_id,
            }
        },
    )

    response.headers["Retry-After"] = str(
        retry_after
    )

    return response


async def rate_limit_middleware(
    request: Request,
    call_next,
):
    if request.method == "OPTIONS":
        return await call_next(request)

    client_key = _get_client_key(request)
    rule = _get_rule(request)

    allowed, retry_after = (
        rate_limiter.is_allowed(
            client_key,
            rule,
        )
    )

    if not allowed:

        if rule is AUTH_RULE:
            rule_name = "auth"
        elif rule is UPLOAD_RULE:
            rule_name = "upload"
        else:
            rule_name = "default"

        RATE_LIMIT_EXCEEDED_TOTAL.labels(
            rule=rule_name,
        ).inc()

        logger.warning(
            "Rate limit exceeded | rule=%s path=%s",
            rule_name,
            request.url.path,
        )

        return _rate_limit_response(
            request,
            retry_after,
        )

    response = await call_next(request)

    response.headers["X-RateLimit-Limit"] = str(
        rule.requests
    )

    return response