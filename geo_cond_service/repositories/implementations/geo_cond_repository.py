import httpx

import geo_cond_service.schemas.geo_cond_schemas as schemas
from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NATURA2000_URL =  "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"



class GeoCondRepository(GeoCondRepositoryInterface):
    async def get_power_infrastructure(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultPower:
        query = f"""
        [out:json];
        (
          node(around:{radius},{lat},{lng})[power=substation];
          way(around:{radius},{lat},{lng})[power=line];
          relation(around:{radius},{lat},{lng})[power=line];
        );
        out center;
        """

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(OVERPASS_URL, data=query)
            response.raise_for_status()
            response = response.json()
            print(response)

        return schemas.GeoCondResultPower(
            near_powerline=False,
            has_substation=False
        )

    # todo: implement actual logic
    async def get_protected_areas(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultProtection: 
        return schemas.GeoCondResultProtection(
            in_protected_area=False
        )

    # todo: implement actual logic
    async def get_buildings_in_area(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultBuildings:
        return schemas.GeoCondResultBuildings(
            urban_building_density=0.0,
            on_existing_building=False
        )

    # todo: implement actual logic
    async def get_forest_overlap(
        self, lat: float, lng: float, radius: int
    ) -> schemas.GeoCondResultForest:
        return schemas.GeoCondResultForest(
            forest_coverage_percent=0.0
        )