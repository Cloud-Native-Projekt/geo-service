from fastapi import APIRouter, Depends

from geo_cond_service.dependencies import get_geo_cond_service
from geo_cond_service.schemas.geo_cond_schemas import GeoCond
from geo_cond_service.services.geo_cond_service import GeoCondService

router = APIRouter()


@router.get("/geo/power", status_code=200)
async def geo_cond_power_endpoint(lat: float, lng: float, radius: int, geo_cond_service: GeoCondService = Depends(get_geo_cond_service)):
    geo_cond = GeoCond(lat=lat, lng=lng, radius=radius)
    return await geo_cond_service.get_power(geo_cond)


@router.get("/geo/protection", status_code=200)
async def geo_cond_protection_endpoint(lat: float, lng: float, radius: int, geo_cond_service: GeoCondService = Depends(get_geo_cond_service)):
    geo_cond = GeoCond(lat=lat, lng=lng, radius=radius)
    return await geo_cond_service.get_protected_areas(geo_cond)


@router.get("/geo/forest", status_code=200)
async def geo_cond_forest_endpoint(lat: float, lng: float, radius: int, geo_cond_service: GeoCondService = Depends(get_geo_cond_service)):
    geo_cond = GeoCond(lat=lat, lng=lng, radius=radius)
    return await geo_cond_service.get_forest_overlap(geo_cond)


@router.get("/geo/builtup", status_code=200)
async def geo_cond_builtup_endpoint(lat: float, lng: float, radius: int, geo_cond_service: GeoCondService = Depends(get_geo_cond_service)):
    geo_cond = GeoCond(lat=lat, lng=lng, radius=radius)
    return await geo_cond_service.get_buildings_in_area(geo_cond)
