from fastapi import Depends

from geo_cond_service.repositories.implementations.geo_cond_repository import (
    GeoCondRepository,
)
from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)
from geo_cond_service.services.geo_cond_service import GeoCondService


async def get_geo_cond_repository() -> GeoCondRepositoryInterface:
    return GeoCondRepository()

async def get_geo_cond_service(geo_cond_repository: GeoCondRepositoryInterface = Depends(get_geo_cond_repository)):
    return GeoCondService(geo_cond_repository)

