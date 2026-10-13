from fastapi import FastAPI
from app.database import initialize_database
from fastapi.middleware.cors import CORSMiddleware
from app.routes.products import router as products_router
from app.routes.product_variants import router as product_variants_router
from app.routes.locations import router as locations_router
from app.routes.sources import router as sources_router
from app.routes.price_observations import router as price_observations_router
from app.routes.search import router as search_router
from app.routes.price_analysis import router as price_analysis_router
from app.routes.feedback import router as feedback_router
from fastapi.staticfiles import StaticFiles
from app.routes.uploads import router as uploads_router
from app.routes.comments import router as comments_router
from app.routes.posts import router as posts_router
from app.routes.reactions import router as reactions_router
from app.routes.users import router as users_router
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import (configure_logging, logging_middleware,)
from app.middleware.cors import configure_cors
from app.middleware.rate_limit import rate_limit_middleware
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.metrics import router as metrics_router
from app.queue import task_queue
from pathlib import Path
from fastapi.staticfiles import StaticFiles


import logging

logger = logging.getLogger("pricebiz")

configure_logging()

app = FastAPI()

register_exception_handlers(app)

app.middleware("http")(rate_limit_middleware)

configure_cors(app)

app.middleware("http")(logging_middleware)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads",
)


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(products_router)
app.include_router(product_variants_router)
app.include_router(locations_router)
app.include_router(sources_router)
app.include_router(price_observations_router)
app.include_router(search_router)
app.include_router(price_analysis_router)
app.include_router(feedback_router)
app.include_router(uploads_router)
app.include_router(comments_router)
app.include_router(posts_router)
app.include_router(reactions_router)
app.include_router(users_router)


@app.on_event("startup")
async def startup():
    logger.info("Starting PriceBiz API")

    try:
        await initialize_database()

        await task_queue.start()

        logger.info("Database initialization completed")

    except Exception:
        logger.exception("Application startup failed")
        raise


@app.get("/")
async def root():
    return {"message": "PriceBiz API is running"}

@app.on_event("shutdown")
async def shutdown():
    logger.info("Stopping PriceBiz API")

    await task_queue.stop()

    logger.info("PriceBiz API stopped")