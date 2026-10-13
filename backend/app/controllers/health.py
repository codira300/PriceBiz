from app.services import health as health_service


async def get_health():
    return await health_service.get_health()


async def get_readiness():
    return await health_service.get_readiness()