import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.controllers import health as health_controller
from app.services.health import HealthCheckError


logger = logging.getLogger("pricebiz")

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health():
    return await health_controller.get_health()


@router.get("/ready")
async def readiness():
    try:
        return await health_controller.get_readiness()

    except HealthCheckError as exc:
        logger.error("Readiness check failed: %s", exc)

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "pricebiz",
                "database": "unavailable",
            },
        )
        

