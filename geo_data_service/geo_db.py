import os
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from geoalchemy2 import WKTElement
from geo_data_service.geo_models import Base, Substation, PowerLine, ProtectedArea, Forests, Building
import requests
import asyncpg

requests.packages.urllib3.disable_warnings()
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

BUNDESLAENDER = [
    "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg",
    "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen",
    "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"
]

class GeoDB:
    __USER = os.getenv("POSTGRES_USER")
    __PASSWORD = os.getenv("POSTGRES_PASSWORD")
    __HOST = os.getenv("POSTGRES_HOST")
    __PORT = os.getenv("POSTGRES_PORT")
    __DATABASE = os.getenv("POSTGRES_DB")
    
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__engine = create_async_engine(f"postgresql+asyncpg://{self.__USER}:{self.__PASSWORD}@{self.__HOST}:{self.__PORT}/{self.__DATABASE}")
        self.SessionLocal = sessionmaker(bind=self.__engine, class_=AsyncSession, expire_on_commit=False)
        
        
    def extract_coordinates_from_way(self, way):
        """
        Extract coordinates from an OSM way.
        Returns a list of dictionaries with 'lon' and 'lat'.
        """
        coords = []
        coordinates = way.get("geometry", [])
        for coord in coordinates:
            coords.append({'lon': coord['lon'], 'lat': coord['lat']})
        return coords

    def extract_geometry_from_way(self, way):
        coords = self.extract_coordinates_from_way(way)  # Extract coordinates for the way
        # Polygon requires at least 4 points (first == last)
        if coords and len(coords) >= 3:
            if coords[0] != coords[-1]:  # Ensure the polygon is closed
                coords.append(coords[0])
            if len(coords) >= 4:
                polygon_wkt = "POLYGON((" + ", ".join(f"{c['lon']} {c['lat']}" for c in coords) + "))"
                return WKTElement(polygon_wkt, srid=4326)
            
            
    def extract_multipolygon_from_relation(self, relation):
        """
        Extract MultiPolygon geometry from an OSM relation, including nested relations.
        """
        polygons = []

        for member in relation.get("members", []):
            if member["type"] == "way":
                coords = self.extract_coordinates_from_way(member)
                # Polygon requires at least 4 points (first == last)
                if coords and len(coords) >= 3:
                    if coords[0] != coords[-1]:  # Ensure the polygon is closed
                        coords.append(coords[0])
                    if len(coords) >= 4:
                        polygon_wkt = "POLYGON((" + ", ".join(f"{c['lon']} {c['lat']}" for c in coords) + "))"
                        polygons.append(polygon_wkt)
            elif member["type"] == "relation":
                # Recursively extract geometry from nested relations
                nested_multipolygon = self.extract_multipolygon_from_relation(member)
                if nested_multipolygon:
                    polygons.append(nested_multipolygon)

        # Combine all polygons into a MULTIPOLYGON
        if polygons:
            multipolygon_wkt = "MULTIPOLYGON(((" + "), (".join(polygon.strip("POLYGON()") for polygon in polygons) + ")))"
            return WKTElement(multipolygon_wkt, srid=4326)

        return None


    async def fill_table_substations(self) -> None:
        self.logger.info("Filling substations table...")
        await self._fill_table(
            BUNDESLAENDER,
            """
            [out:json][timeout:25];
            area[name="{name}"];
            node["power"="substation"](area);
            out geom;
            """,
            self._process_substation
        )

    async def fill_table_buildings(self) -> None:
        self.logger.info("Filling buildings table...")
        tags_of_interest = [{"landuse": "residential"}, {"landuse": "commercial"}]
        for tags in tags_of_interest:
            tag_key, tag_value = list(tags.items())[0]
            await self._fill_table(
                BUNDESLAENDER,
                f"""
                [out:json];
                area[name="{{name}}"];
                way["{tag_key}"="{tag_value}"](area);
                out geom;
                """,
                self._process_building            
            )
            await self._fill_table(
                BUNDESLAENDER,
                f"""
                [out:json];
                area[name="{{name}}"];
                rel["{tag_key}"="{tag_value}"](area);
                out geom;
                """,
                self._process_building            
            )

    async def fill_table_power_lines(self) -> None:
        self.logger.info("Filling power_lines table...")
        await self._fill_table(
            BUNDESLAENDER,
            """
            [out:json][timeout:25];
            area[name="{name}"];
            way["line"="busbar"]["power"="line"](area);
            out geom;
            """,
            self._process_power_line        
        )

    async def fill_table_protected_areas(self) -> None:
        self.logger.info("Filling protected_areas table...")
        await self._fill_table(
            BUNDESLAENDER,
            """
            [out:json][timeout:25];
            area[name="{name}"];
            way["boundary"="protected_area"](area);
            rel["boundary"="protected_area"](area);
            out geom;
            """,
            self._process_protected_area       
        )

    async def fill_table_forests(self) -> None:
        self.logger.info("Filling forest table...")
        tags_of_interest = [{"natural": "wood"}, {"landuse": "forest"}, {"landcover": "trees"}]
        for tags in tags_of_interest:
            tag_key, tag_value = list(tags.items())[0]
            await self._fill_table(
                BUNDESLAENDER,
                f"""
                [out:json];
                area[name="{{name}}"];
                way["{tag_key}"="{tag_value}"](area);
                out geom;
                """,
                self._process_forests            
            )
            await self._fill_table(
                BUNDESLAENDER,
                f"""
                [out:json];
                area[name="{{name}}"];
                rel["natural"="wood"](area);
                out geom;
                """,
                self._process_forests,
            )

    async def _fill_table(self, bundeslaender, query_template, process_func):
        async with self.SessionLocal() as session:
            for name in bundeslaender:
                query = query_template.format(name=name)
                response = requests.get(OVERPASS_URL, params={'data': query}, verify=False)
                if response.status_code == 200:
                    elements = response.json().get('elements', [])
                    self.logger.info(f"Fetched {len(elements)} elements for {name}")
                    for el in elements:
                        obj = process_func(el)
                        if obj:
                            session.add(obj)
                    await session.commit()
                else:
                    self.logger.error(f"Error fetching data for {name}: {response.status_code}")

    def _process_substation(self, el):
        geom = WKTElement(f"POINT({el['lon']} {el['lat']})", srid=4326)
        return Substation(osm_id=el.get("id"), geom=geom)

    def _process_power_line(self, el):
        coords = el.get("geometry", [])
        if coords:
            line_wkt = "LINESTRING(" + ", ".join(f"{c['lon']} {c['lat']}" for c in coords) + ")"
            geom = WKTElement(line_wkt, srid=4326)
            return PowerLine(osm_id=el.get("id"), geom=geom)
        return None

    def _process_protected_area(self, el):
        tags = el.get("tags", {})
        osm_id= el.get("id")
        designation = tags.get("protection_title", "No Designation")
        if el["type"] == "relation":
            geom = self.extract_multipolygon_from_relation(el)
            if geom:
                return ProtectedArea(osm_id=osm_id, geom=geom, designation=designation)
        elif el["type"] == "way":
            geom = self.extract_geometry_from_way(el)
            if geom:
                return ProtectedArea(osm_id=osm_id, geom=geom, designation=designation)
        return None

    def _process_building(self, el):
        tags = el.get("tags", {})
        osm_id= el.get("id")
        if el["type"] == "relation":
            geom = self.extract_multipolygon_from_relation(el)
            if geom:
                return Building(osm_id=osm_id, geom=geom)
        elif el["type"] == "way":
            geom = self.extract_geometry_from_way(el)
            if geom:
                return Building(osm_id=osm_id, geom=geom)
        elif el["type"] == "node":
            geom = WKTElement(f"POINT({el['lon']} {el['lat']})", srid=4326)
            return Building(osm_id=osm_id, geom=geom)
        return None

    def _process_forests(self, el):
        osm_id= el.get("id")
        type = el.get("tags", {}).get("leaf_type", "Unknown")
        if el["type"] == "relation":
            geom = self.extract_multipolygon_from_relation(el)
            if geom:
                return Forests(osm_id=osm_id, type=type, geom=geom)
        elif el["type"] == "way":
            geom = self.extract_geometry_from_way(el)
            if geom:
                return Forests(osm_id=osm_id, type=type, geom=geom)
        elif el["type"] == "node":
            geom = WKTElement(f"POINT({el['lon']} {el['lat']})", srid=4326)
            return Forests(osm_id=osm_id, type=type, geom=geom)
        return None
    
    async def fill_all_tables(self) -> None:
        """
        Fill all tables with data from Overpass API.
        """
        await self.fill_table_substations()
        await self.fill_table_power_lines()
        await self.fill_table_protected_areas()
        await self.fill_table_forests()
        await self.fill_table_buildings()

    async def create_tables(self) -> None:
        """
        Create required tables in the database if they do not exist.
        """
        async with self.__engine.begin() as conn:
            required_tables = ['substations', 'power_lines', 'protected_areas', 'forests', 'buildings']
            existing_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            for table in required_tables:
                if table not in existing_tables:
                    await conn.run_sync(Base.metadata.tables[table].create)
                    self.logger.info(f"Table {table} created.")
                else:
                    self.logger.info(f"Table {table} already exists.")

    async def delete_tables(self) -> None:
        """
        Delete required tables from the database if they exist.
        """
        async with self.__engine.begin() as conn:
            required_tables = ['substations', 'power_lines', 'protected_areas', 'forests', 'buildings']
            existing_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            for table in required_tables:
                if table in existing_tables:
                    await conn.run_sync(Base.metadata.tables[table].drop)
                    self.logger.info(f"Table {table} deleted.")
                else:
                    self.logger.info(f"Table {table} does not exist, skipping deletion.")

async def main():
    """
    Main entry point for creating tables and filling them with data.
    """
    db = GeoDB()
    await db.delete_tables()  # Uncomment if you want to delete existing tables
    await db.create_tables()
    await db.fill_all_tables()

if __name__ == "__main__":
    asyncio.run(main())