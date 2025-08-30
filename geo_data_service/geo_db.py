import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, text
from typing import AsyncGenerator, Any
from geo_data_service.geo_models import Base
import logging
import urllib3
import asyncio
import certifi
import requests
from geoalchemy2 import WKTElement
from geo_data_service.geo_models import Substation, PowerLine, ProtectedArea, ForestCover, Building
requests.packages.urllib3.disable_warnings() 

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


class GeoDB:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(name=self.__class__.__name__)
        self.download_dir = "/geo_data_service/app/data" 
        # Use asyncpg as the async driver
        self.__engine = create_async_engine(os.getenv("DATABASE_URL"))
        self.SessionLocal = sessionmaker(bind=self.__engine, class_=AsyncSession, expire_on_commit=False)
        # source: https://wiki.openstreetmap.org/wiki/Germany/Grenzen
        self.bundeslaender = [
            {"name": "Baden-Württemberg"},
            {"name": "Bayern"},
            {"name": "Berlin"},
            {"name": "Brandenburg"},
            {"name": "Bremen"},
            {"name": "Hamburg"},
            {"name": "Hessen"},
            {"name": "Mecklenburg-Vorpommern"},
            {"name": "Niedersachsen"},
            {"name": "Nordrhein-Westfalen"},
            {"name": "Rheinland-Pfalz"},
            {"name": "Saarland"},
            {"name": "Sachsen"},
            {"name": "Sachsen-Anhalt"},
            {"name": "Schleswig-Holstein"},
            {"name": "Thüringen"},
        ]
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.SessionLocal() as session:
            yield session

    def extract_geometry_from_relation(self, relation):
        """Extrahiert die Geometrie aus einer Relation."""
        coords = []
        for member in relation.get("members", []):
            if member["type"] == "way":
                coords.extend(member.get("geometry", []))
            if member["type"] == "relation":
                nested_geom = self.extract_geometry_from_relation(member)
                if nested_geom:
                    coords.extend(nested_geom)
            elif member["type"] == "node":
                coords.append(member)  # Knoten können auch relevante Geometrie sein

        if coords:
            if coords[0]['lon'] != coords[-1]['lon'] or coords[0]['lat'] != coords[-1]['lat']:
                coords.append(coords[0])
            # Erstellen eines MultiPolygon basierend auf den Koordinaten
            polygon_wkt = "MultiPolygon((" + ", ".join(f"{c['lon']} {c['lat']}" for c in coords) + "))"
            return WKTElement(polygon_wkt, srid=4326)
        return None
    
    async def get_geo_data(self) -> Any:
        return

    # need to call for each table separately because api response is too large
    async def fill_table_substations(self) -> None:
        async with self.SessionLocal() as session:
            for bundesland in self.bundeslaender:
                query =  f"""
                    [out:json][timeout:25];
                    area[name="{bundesland["name"]}"];
                    node["power"="substation"](area);
                    out geom;
                    """
                response = requests.get(OVERPASS_URL, params={'data': query}, verify=False)
                if response.status_code == 200:
                    elements = response.json().get('elements', [])
                    self.logger.info(f"Fetched {len(elements)} substation elements for {bundesland['name']}")
                    for el in elements:
                        tags = el.get("tags", {})
                        if el["type"] == "node" and tags.get("power") == "substation":
                            lat_node = el["lat"]
                            lon_node = el["lon"]
                            id = tags.get("id")
                            geom = WKTElement(f"POINT({lon_node} {lat_node})", srid=4326)
                            session.add(Substation(id=id, geom=geom))
                    await session.commit()
                else:
                    self.logger.error(f"Error calling substation data for {bundesland['name']}: {response.status_code}")
                    return

    async def fill_table_power_lines(self) -> None:
        async with self.SessionLocal() as session:
            for bundesland in self.bundeslaender:
                query =  f"""
                    [out:json][timeout:25];
                    area[name="{bundesland["name"]}"];
                    way["line"="busbar"]["power"="line"](area);
                    out geom;
                    """
                response = requests.get(OVERPASS_URL, params={'data': query}, verify=False)
                if response.status_code == 200:
                    elements = response.json().get('elements', [])
                    self.logger.info(f"Fetched {len(elements)} power-line elements for {bundesland['name']}")
                    for el in elements:
                        tags = el.get("tags", {})
                        if el["type"] in ['way'] and tags.get("power") == "line":
                            coords = el.get("geometry", [])
                            if coords:
                                line_wkt = "LINESTRING(" + ", ".join(f"{c['lon']} {c['lat']}" for c in coords) + ")"
                                geom = WKTElement(line_wkt, srid=4326)
                                id = el.get("id")
                            else:
                                continue
                            session.add(PowerLine(id=id, geom=geom))
                    await session.commit()
                else:
                    self.logger.error(f"Error calling power line data for {bundesland['name']}: {response.status_code}")
                    return

    async def fill_table_protected_areas(self) -> None:
        async with self.SessionLocal() as session:
            for bundesland in self.bundeslaender:
                query =  f"""
                    [out:json][timeout:25];
                    area[name="{bundesland["name"]}"];
                    way["boundary"="protected_area"](area);
                    rel["boundary"="protected_area"](area);
                    out geom;
                    """
                response = requests.get(OVERPASS_URL, params={'data': query}, verify=False)
                if response.status_code == 200:
                    elements = response.json().get('elements', [])
                    self.logger.info(f"Fetched {len(elements)} protected-area elements for {bundesland}")
                    for el in elements:
                        tags = el.get("tags", {})
                        id = el.get("id")
                        designation = tags.get("protection_title")
                        if el["type"]=="relation":
                            member_nr=0
                            for member in el.get("members", []):
                                member_nr = member_nr + 1
                                id = int(str(id)+ str(member_nr))
                                geom = self.extract_geometry_from_relation(member)
                                if geom:
                                    session.add(ProtectedArea(id=id, geom=geom, designation=designation))
                        elif el["type"]=="way":
                            geom = self.extract_geometry_from_relation(el)
                            if geom:
                                session.add(ProtectedArea(id=id, geom=geom, designation=designation))
                    await session.commit()
                else:
                    self.logger.error(f"Error calling protected area data for {bundesland}: {response.status_code}")
                    return

    async def create_tables(self) -> None:

        async with self.__engine.begin() as conn:
            required_tables = ['substations', 'power_lines', 'protected_areas', 'forest_cover', 'buildings']
            existing_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

            for table in required_tables:
                if table not in existing_tables:
                    await conn.run_sync(Base.metadata.tables[table].create)
                    self.logger.info(f"Table {table} created.")
                else:
                    self.logger.info(f"Table {table} already exists.")
    async def delete_tables(self) -> None:
        async with self.__engine.begin() as conn:
            required_tables = ['substations', 'power_lines', 'protected_areas', 'forest_cover', 'buildings']
            existing_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

            for table in required_tables:
                if table in existing_tables:
                    await conn.run_sync(Base.metadata.tables[table].drop)
                    self.logger.info(f"Table {table} deleted.")
                else:
                    self.logger.info(f"Table {table} does not exist, skipping deletion.")
                    
async def main():
    print("WORKS!")
    db = GeoDB()
    await db.delete_tables()
    await db.create_tables()
    #await db.fill_table_substations()
    #await db.fill_table_power_lines()
    await db.fill_table_protected_areas()
    #await db.get_geo_data()

if __name__ == "__main__":
    asyncio.run(main())