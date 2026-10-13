import logging
import time
import uuid

from fastapi import Request

from app.monitoring.metrics import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
)


logger = logging.getLogger("pricebiz")


def configure_logging():
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


async def logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        duration = time.perf_counter() - start_time

        logger.exception(
            "Request failed | "
            "request_id=%s method=%s path=%s "
            "duration=%.3fs",
            request_id,
            request.method,
            request.url.path,
            duration,
        )

        raise

    duration = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id

    route = request.scope.get("route")

    route_path = getattr(
        route,
        "path",
        request.url.path,
    )

    status = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        route=route_path,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        route=route_path,
    ).observe(duration)

    if response.status_code >= 400:
        HTTP_ERRORS_TOTAL.labels(
            method=request.method,
            route=route_path,
            status=status,
        ).inc()

    if response.status_code >= 500:
        logger.error(
            "Request completed | "
            "request_id=%s method=%s path=%s "
            "status=%s duration=%.3fs",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    elif response.status_code >= 400:
        logger.warning(
            "Request completed | "
            "request_id=%s method=%s path=%s "
            "status=%s duration=%.3fs",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    else:
        logger.info(
            "Request completed | "
            "request_id=%s method=%s path=%s "
            "status=%s duration=%.3fs",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    return response