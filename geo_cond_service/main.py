import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from geo_cond_service.routes import geo_cond_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before application startup)
    logger.info("Running startup tasks...")
    logger.info("Startup tasks completed")
    yield
    # Shutdown code (runs after application shutdown)
    logger.info("Running shutdown tasks...")
    logger.info("Shutdown tasks completed")
    # This is where you put code that was previously in @app.on_event("shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(geo_cond_router.router)
