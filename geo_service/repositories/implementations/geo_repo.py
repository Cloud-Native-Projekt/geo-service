import httpx
from geoalchemy2 import WKTElement
from sqlalchemy import func, select

from geo_service.data.db import async_session
from geo_service.data.geo_models import PowerLine, Substation
from geo_service.repositories.interfaces.iface_geo_repo import GeoRepoInterface
from geo_service.schemas.geo_schemas import (
    ResultBuildings,
    ResultForest,
    ResultPower,
    ResultProtection,
)

NATURA2000_URL = "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


class GeoRepo(GeoRepoInterface):
    """Check if power infrastructure exists in PostGIS within radius.
    If not, fetch from Overpass API and store in PostGIS.
    Returns nearest distances to substation and powerline.
    """

    async def get_power_infrastructure(
        self, lat: float, lng: float, radius: int
    ) -> ResultPower:

        point = WKTElement(f"POINT({lng} {lat})", srid=4326)

        async with async_session() as session:
            # 1️⃣ Check if Substations exist
            exists_query = select(func.count(Substation.id)).where(
                Substation.geom.ST_DWithin(point, radius)
            )
            res = await session.execute(exists_query)
            if res.scalar() == 0:
                # Fetch from Overpass API
                query = f"""
                [out:json];
                (
                    node(around:{radius},{lat},{lng})[power=substation];
                    way(around:{radius},{lat},{lng})[power=line];
                    relation(around:{radius},{lat},{lng})[power=line];
                );
                out center;
                """
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(OVERPASS_URL, data={"data": query})
                    response.raise_for_status()
                    data = response.json()

                # Prepare data
                substations_to_add = []
                powerlines_to_add = []

                for element in data.get("elements", []):
                    tags = element.get("tags", {})
                    if element["type"] == "node" and tags.get("power") == "substation":
                        lat_node = element["lat"]
                        lon_node = element["lon"]
                        name = tags.get("name")
                        geom = WKTElement(f"POINT({lon_node} {lat_node})", srid=4326)
                        substations_to_add.append(Substation(name=name, geom=geom))
                    elif (
                        element["type"] in ["way", "relation"]
                        and tags.get("power") == "line"
                    ):
                        center = element.get("center")
                        if center:
                            lat_line = center["lat"]
                            lon_line = center["lon"]
                            name = tags.get("name")
                            voltage = tags.get("voltage")
                            geom = WKTElement(
                                f"POINT({lon_line} {lat_line})", srid=4326
                            )
                            powerlines_to_add.append(
                                PowerLine(
                                    name=name,
                                    voltage_kv=float(voltage) if voltage else None,
                                    geom=geom,
                                )
                            )

                # Insert into PostGIS
                async with session.begin():
                    session.add_all(substations_to_add + powerlines_to_add)

            # Compute nearest distances
            nearest_substation_query = (
                select(Substation.geom.ST_Distance(point).label("distance"))
                .order_by(Substation.geom.ST_Distance(point))
                .limit(1)
            )
            nearest_powerline_query = (
                select(PowerLine.geom.ST_Distance(point).label("distance"))
                .order_by(PowerLine.geom.ST_Distance(point))
                .limit(1)
            )

            substation_res = await session.execute(nearest_substation_query)
            powerline_res = await session.execute(nearest_powerline_query)

            nearest_substation_distance = substation_res.scalar() or None
            nearest_powerline_distance = powerline_res.scalar() or None

        return ResultPower(
            nearest_substation_distance_m=nearest_substation_distance,
            nearest_powerline_distance_m=nearest_powerline_distance,
        )

    # todo: implement actual logic
    async def get_protected_areas(
        self, lat: float, lng: float, radius: int
    ) -> ResultProtection:
        return ResultProtection(in_protected_area=False)

    # todo: implement actual logic
    async def get_buildings_in_area(
        self, lat: float, lng: float, radius: int
    ) -> ResultBuildings:
        return ResultBuildings(urban_building_density=0.0, on_existing_building=False)

    # todo: implement actual logic
    async def get_forest(self, lat: float, lng: float, radius: int) -> ResultForest:
        return ResultForest(forest_coverage_percent=0.0)
