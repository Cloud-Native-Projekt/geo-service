import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from geo_service.routes import geo_router

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


app = FastAPI(lifespan=lifespan)

app.include_router(geo_router.router)
