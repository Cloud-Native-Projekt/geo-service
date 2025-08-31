import os
import logging
from databases import Database
from sqlalchemy import create_engine, MetaData
from geo_service.repositories.interfaces.iface_geo_repo import GeoRepoInterface

from geo_service.schemas.geo_schemas import (
    ResultBuildings,
    ResultForest,
    ResultPower,
    ResultProtection,
)


class GeoRepo(GeoRepoInterface):
    
    __USER = os.getenv("POSTGRES_USER")
    __PASSWORD = os.getenv("POSTGRES_PASSWORD")
    __HOST = os.getenv("POSTGRES_HOST")
    __PORT = os.getenv("POSTGRES_PORT")
    __DATABASE = os.getenv("POSTGRES_DB")
    
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.geo_db_url = f"postgresql+asyncpg://{self.__USER}:{self.__PASSWORD}@{self.__HOST}:{self.__PORT}/{self.__DATABASE}"
        self.engine = create_engine(self.geo_db_url)
        self.metadata = MetaData()
        self.database = Database(self.geo_db_url)

    async def get_power_infrastructure(self, lat: float, lng: float) -> ResultPower:
        # Query for the nearest substation
        query_substation = """
            WITH p AS (
                SELECT ST_SetSRID(ST_Point(:lng, :lat), 4326) AS pt
            )
            SELECT s.id,
                ST_Distance(s.geom, p.pt)::NUMERIC AS dist_m
            FROM substations s, p
            ORDER BY s.geom <-> p.pt
            LIMIT 1;
        """
        
        # Query for the nearest power line
        query_powerline = """
            WITH p AS (
                SELECT ST_SetSRID(ST_Point(:lng, :lat), 4326) AS pt
            )
            SELECT l.id,
                ST_Distance(l.geom, p.pt)::NUMERIC AS dist_m
            FROM power_lines l, p
            ORDER BY l.geom <-> p.pt
            LIMIT 1;
        """
        
        async with self.database as db:
            # Fetch the nearest substation
            substation = await db.fetch_one(query_substation, values={"lat": lat, "lng": lng})
            # Fetch the nearest power line
            powerline = await db.fetch_one(query_powerline, values={"lat": lat, "lng": lng})

        self.logger.info(f"Substation query result: {substation}")
        self.logger.info(f"Powerline query result: {powerline}")

        # Calculate distances
        nearest_substation_distance_m = float(substation["dist_m"]) if substation and substation["dist_m"] is not None else None
        nearest_powerline_distance_m = float(powerline["dist_m"]) if powerline and powerline["dist_m"] is not None else None

        return ResultPower(
            nearest_substation_distance_m=nearest_substation_distance_m,
            nearest_powerline_distance_m=nearest_powerline_distance_m,
        )
            
    async def get_protected_areas(
        self, lat: float, lng: float
    ) -> ResultProtection:
        query = """
            WITH p AS (
                SELECT ST_SetSRID(ST_Point(:lng, :lat), 4326) AS pt
            )
            SELECT a.designation, a.id
            FROM protected_areas a, p
            WHERE ST_Contains(a.geom, p.pt)
            LIMIT 1;
        """
        async with self.database as db:
            result = await db.fetch_one(query, values={"lat": lat, "lng": lng})
        print(result)
        in_protected_area = result is not None
        designation = result["designation"] if result and "designation" in result else "No Designation"
        return ResultProtection(
            in_protected_area=in_protected_area,
            designation=designation
        )

    async def get_buildings_in_area(
        self, lat: float, lng: float
    ) -> ResultBuildings:
        query = """
            WITH p AS (
                SELECT ST_SetSRID(ST_Point(:lng, :lat), 4326) AS pt
            )
            SELECT b.id
            FROM buildings b, p
            WHERE ST_Contains(b.geom, p.pt)
            LIMIT 1;
        """
        async with self.database as db:
            result = await db.fetch_one(query, values={"lat": lat, "lng": lng})
        in_building_area = result is not None
        return ResultBuildings(
            in_building_area=in_building_area,
        )

    async def get_forest(self, lat: float, lng: float) -> ResultForest:
        query = """
            WITH p AS (
                SELECT ST_SetSRID(ST_Point(:lng, :lat), 4326) AS pt
            )
            SELECT
                f.type, f.id
            FROM forests f, p
            WHERE ST_Contains(f.geom, p.pt)
            LIMIT 1;
        """
        async with self.database as db:
            result = await db.fetch_one(query, values={"lat": lat, "lng": lng})
        in_forest = result is not None
        forest_type = result["type"] if result and "type" in result else "No Forest Type"
        return ResultForest(
            in_forest=in_forest,
            type=forest_type,
        )
