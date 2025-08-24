import geo_cond_service.schemas.geo_cond_schemas as schemas
from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)


class GeoCondService():

    def __init__(self, geo_cond_repository: GeoCondRepositoryInterface):
        self.geo_cond_repository = geo_cond_repository


    async def get_power(self, req: schemas.GeoCond) -> schemas.GeoCondResultPower:

        """Fetch GeoCond data and return as GeoCondResult."""
        power: schemas.GeoCondResultPower = await self.geo_cond_repository.get_power_infrastructure(
            lat=req.lat,
            lng=req.lng,
            radius=req.radius
        )
        if not power:
            raise ValueError("Power infrastructure data not found")
        
        return power


    async def get_protected_areas(self, req: schemas.GeoCond) -> schemas.GeoCondResultProtection:
        """Fetch protected areas data."""
        protection: schemas.GeoCondResultProtection = await self.geo_cond_repository.get_protected_areas(
            lat=req.lat,
            lng=req.lng,
            radius=req.radius
        )
        if not protection:
            raise ValueError("Protected areas data not found")
        return protection

    async def get_forest_overlap(self, req: schemas.GeoCond) -> schemas.GeoCondResultForest:
        """Fetch forest overlap data."""
        forest: schemas.GeoCondResultForest = await self.geo_cond_repository.get_forest_overlap(
            lat=req.lat,
            lng=req.lng,
            radius=req.radius
        )
        if not forest:
            raise ValueError("Forest overlap data not found")
        return forest

    async def get_buildings_in_area(self, req: schemas.GeoCond) -> schemas.GeoCondResultBuildings:
        """Fetch built-up/buildings data."""
        buildings : schemas.GeoCondResultBuildings = await self.geo_cond_repository.get_buildings_in_area(
            lat=req.lat,
            lng=req.lng,
            radius=req.radius
        )
        if not buildings:
            raise ValueError("Buildings in area data not found")
        return buildings