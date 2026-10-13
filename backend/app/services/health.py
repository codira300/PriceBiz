from app.database.connection import database
from app.monitoring.metrics import (
    HEALTH_CHECKS_TOTAL,
    HEALTH_CHECK_FAILURES_TOTAL,
)


status = {
    "status": "ok",
    "service": "pricebiz",
}
class HealthCheckError(Exception):
    pass


async def check_database():
    try:
        await database.command("ping")
        return True
    except Exception as exc:
        raise HealthCheckError("Database is unavailable") from exc


async def get_health():
    HEALTH_CHECKS_TOTAL.labels(
        check="liveness",
    ).inc()

    return {
        **status
    }


async def get_readiness():
    HEALTH_CHECKS_TOTAL.labels(
        check="readiness",
    ).inc()

    try:
        await check_database()

    except HealthCheckError:
        HEALTH_CHECK_FAILURES_TOTAL.labels(
            check="readiness",
        ).inc()

        raise

    return {
        **status,
        "database": "ok",
    }