from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)
from geo_cond_service.schemas.geo_cond_schemas import GeoCond, GeoCondResult
from shared.service_caller import service_post


class GeoCondService():

    def __init__(self, geo_cond_repository: GeoCondRepositoryInterface):
        self.geo_cond_repository = geo_cond_repository


    async def get_geo_conditions(self, req: GeoCond) -> GeoCondResult:
        lat = req.lat
        lon = req.lon
        """Fetch GeoCond data and return as GeoCondResult."""
        power_infrastructure_data = await self.geo_cond_repository.query_power_infrastructure(
            lat=lat,
            lon=lon,
            radius_km=req.radius_km
        )
        
        power_infrastructure_elements = power_infrastructure_data.get("elements", [])
        has_substations = any(el.get("tags", {}).get("power") == "substation" for el in power_infrastructure_elements)
        has_power_lines = any(el.get("tags", {}).get("power") == "line" for el in power_infrastructure_elements)
        
        protected_area_data = await self.geo_cond_repository.check_protected_area(
            lat=lat,
            lon=lon,
        )

        used_area_data = await self.geo_cond_repository.check_is_area_used(
            lat=lat,
            lon=lon,
            radius_km=req.radius_km
        )

        forest_coverage_percent = used_area_data.get("forest_coverage_percent", 0.0)
        urban_building_density = used_area_data.get("urban_building_density", 0.0)
        on_existing_building = used_area_data.get("on_existing_building", True)

        return GeoCondResult(
            near_powerline=has_power_lines,
            has_substation=has_substations,
            in_nature_reserve=protected_area_data,
            forest_coverage_percent=forest_coverage_percent,
            urban_building_density=urban_building_density,
            on_existing_building=on_existing_building
        )
