from fastapi import APIRouter, Depends

from geo_cond_service.dependencies import get_geo_cond_service
from geo_cond_service.schemas.geo_cond_schemas import GeoCond
from geo_cond_service.services.geo_cond_service import GeoCondService

router = APIRouter()


@router.post("/geo-cond", status_code=200)
async def geo_cond_endpoint(geo_cond: GeoCond, geo_cond_service: GeoCondService = Depends(get_geo_cond_service)):
    return await geo_cond_service.get_geo_conditions(geo_cond)
