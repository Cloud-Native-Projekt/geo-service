import httpx
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from geo_data_service.geo_models import Base
from geo_data_service.geo_models import PowerLine, Substation 
from sqlalchemy import insert
import json

NATURA2000_URL = "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"



class DataMaintenance:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def data_exists(self, table_name: str) -> bool:
        #result = await self.db_session.execute(f"SELECT COUNT(*) FROM {table_name}")
        #count = result.scalar()
        #return count > 0
        return


    async def insert_data_power(self, data: json) -> None:           
        substations = []
        power_lines = []

        if data.get('elements'):
            for element in data['elements']:
                if element['type'] == 'node' and 'substation' in element['tags']:
                    substation = Substation(
                        id=element['id'],
                        geom=f"POINT({element['lon']} {element['lat']})"  # Geometrie im WKT-Format
                    )
                    substations.append(substation)

                elif element['type'] == 'way' and 'power' in element['tags']:  # Ändern Sie 'node' zu 'way'
                    # Nehmen Sie an, dass die Nodes für den Weg in element['nodes'] sind
                    line_coords = ', '.join([f"{node['lon']} {node['lat']}" for node in element['nodes']])
                    power_line = PowerLine(
                        id=element['id'],
                        geom=f"LINESTRING({line_coords})"  # Geometrie im WKT-Format
                    )
                    power_lines.append(power_line)

        # Einfügen der Substation-Daten
        if substations:
            stmt = insert(Substation).values([
                {'id': s.id, 'geom': s.geom} for s in substations
            ])
            await self.db_session.execute(stmt)

        # Einfügen der PowerLine-Daten
        if power_lines:
            stmt = insert(PowerLine).values([
                {'id': l.id, 'geom': l.geom} for l in power_lines
            ])
            await self.db_session.execute(stmt)

        await self.db_session.commit()

    async def get_forest_areas(self):
        return
        
    async def get_power_substations(self):
       return

    async def update_table_substation(self):
        return

        
    async def fetch_data_natura2000(self):
        return
       
    async def update_tables_natura2000(self):
        return
    
    async def update_tables(self):
        #await self.update_table_substation()
        #await self.update_tables_natura2000()
        self.logger.info("Updating tables with new data...")
        return

    async def periodic_update(self):
       # while True:
         #   self.logger.info("Starting periodic update...")
         #   await self.update_tables()
         #   await asyncio.sleep(172800)  # wait 2 days
        return
            
