import httpx
from geoalchemy2 import WKTElement
from sqlalchemy import func, select
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncpg  # Async PostgreSQL client
import os
import logging
#from geo_service.data.db import async_session
#from geo_service.data.geo_models import PowerLine, Substation
from geo_service.repositories.interfaces.iface_geo_repo import GeoRepoInterface
from geo_service.schemas.geo_schemas import (
    ResultBuildings,
    ResultForest,
    ResultPower,
    ResultProtection,
)

NATURA2000_URL = "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DATABASE_URL = os.getenv("DATABASE_URL")  # z.B. postgresql://user:password@localhost/dbname


class GeoRepo(GeoRepoInterface):
    """Check if power infrastructure exists in PostGIS within radius.
    If not, fetch from Overpass API and store in PostGIS.
    Returns nearest distances to substation and powerline.
    """
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(name=self.__class__.__name__)

    async def get_power_infrastructure(self, lat: float, lng: float, radius: int)-> ResultPower:
        query = f"""
            [out:json];
                (
                node["substation"](around:{radius}, {lat}, {lng});
                way["substation"](around:{radius}, {lat}, {lng});
                relation["substation"](around:{radius}, {lat}, {lng});
                node[power=line](around:{radius}, {lat}, {lng});
                way[power=line](around:{radius}, {lat}, {lng});
                relation[power=line](around:{radius}, {lat}, {lng});
                );
                out center;
            """
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(OVERPASS_URL, data={"data": query})
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error fetching data from Overpass API")
            else:
                self.logger.info(response.json())
                data = response.json()
                substations = []
        
        db = GeoDB()
        data_maintenance = DataMaintenance(db_session=db.get_db)
        async for session in db.get_db():
            data_maintenance = DataMaintenance(session)
            await data_maintenance.insert_data_power(data)
        
        return ResultPower(
            nearest_substation_distance_m=1000.0,
            nearest_powerline_distance_m=500.0,
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
