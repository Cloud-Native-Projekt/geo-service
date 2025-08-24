import httpx

import geo_service.schemas.geo_schemas as schemas
from geo_service.repositories.interfaces.iface_geo_repo import GeoRepoInterface

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NATURA2000_URL = "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"


class GeoRepo(GeoRepoInterface):
    async def get_power_infrastructure(
        self, lat: float, lng: float, radius: int
    ) -> schemas.ResultPower:
        query = f"""
        [out:json];
        (
        (
          node(around:{radius},{lat},{lng})[power=substation];
          way(around:{radius},{lat},{lng})[power=line];
          relation(around:{radius},{lat},{lng})[power=line];
        );
        out center;
        """
        """
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(OVERPASS_URL, data=query)
            response.raise_for_status()
            response = response.json()
            print(response)
            """

        return schemas.ResultPower(near_powerline=False, has_substation=False)

    # todo: implement actual logic
    async def get_protected_areas(
        self, lat: float, lng: float, radius: int
    ) -> schemas.ResultProtection:
        return schemas.ResultProtection(in_protected_area=False)

    # todo: implement actual logic
    async def get_buildings_in_area(
        self, lat: float, lng: float, radius: int
    ) -> schemas.ResultBuildings:
        return schemas.ResultBuildings(
            urban_building_density=0.0, on_existing_building=False
        )

    # todo: implement actual logic
    async def get_forest(
        self, lat: float, lng: float, radius: int
    ) -> schemas.ResultForest:
        return schemas.ResultForest(forest_coverage_percent=0.0)
