from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)
from geo_cond_service.schemas.geo_cond_schemas import GeoCond, GeoCondResultPower
from shared.service_caller import service_get


class GeoCondService():

    def __init__(self, geo_cond_repository: GeoCondRepositoryInterface):
        self.geo_cond_repository = geo_cond_repository


    async def get_power(self, req: GeoCond) -> GeoCondResultPower:

        """Fetch GeoCond data and return as GeoCondResult."""
        power: GeoCondResultPower = await self.geo_cond_repository.query_power_infrastructure(
            lat=req.lat,
            ln=req.lng,
            radius=req.radius
        )
        if not power:
            raise ValueError("Power infrastructure data not found")
        
        return power
