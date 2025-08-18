import math
from typing import Any

import httpx
import requests
from geojson import FeatureCollection
from shapely.geometry import Point, shape

from geo_cond_service.repositories.interfaces.iface_geo_cond_repository import (
    GeoCondRepositoryInterface,
)
from geo_cond_service.schemas.geo_cond_schemas import GeoCond, GeoCondResultPower

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NATURA2000_URL =  "https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer/2/query"



class GeoCondRepository(GeoCondRepositoryInterface):
  
    async def query_power_infrastructure(self, lat: float, lng: float, radius: int) -> GeoCondResultPower:
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
        
        return GeoCondResultPower(
            near_powerline=False,
            has_substation=5.0
        )

    async def check_protected_area(self, lat: float, lng: float) -> Any:
        params = {
            "geometry": f"{lng},{lat}",                    
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",                                  
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json"
        }
        r = requests.get(NATURA2000_URL, params=params)
        r.raise_for_status()
        geojson = r.json()
        features = geojson.get("features", [])
        if features: # potetally multiple features
            props = features[0]["attributes"]
            print("Gefunden:", props["SITECODE"], props["SITENAME"])
            return True
        else:
            print("Kein Schutzgebiet")
            return False

    async def check_is_area_used(self, lat: float, lng: float, radius: int) -> Any:
        query = f"""
        [out:json][timeout:25];
        (
          way(around:{radius},{lat},{lng})[landuse=forest];
          way(around:{radius},{lat},{lng})[natural=wood];
          way(around:{radius},{lat},{lng})[building];
        );
        out body geom;
        """

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(OVERPASS_URL, data=query)
            res.raise_for_status()
            data = res.json()

        forest_area = 0.0
        buildings = 0
        on_existing_building = False

        point = Point(lng, lat)

        for el in data.get("elements", []):
            if el["type"] == "way" and "geometry" in el:
                coords = [(p["lng"], p["lat"]) for p in el["geometry"]]
                if coords[0] != coords[-1]:  # not closed polygon
                    continue

                try:
                    polygon = shape({"type": "Polygon", "coordinates": [coords]})
                except Exception:
                    continue

                if "landuse" in el["tags"] or "natural" in el["tags"]:
                    forest_area += polygon.area  # in degrees, not m²
                elif "building" in el["tags"]:
                    buildings += 1
                    if polygon.contains(point):
                        on_existing_building = True

        # Fläche des Suchradius (Kreis)
        circle_area_km2 = math.pi * (radius ** 2)

        # Überschätzung in EPSG:4326 — optional: auf metrische Projektion umstellen
        forest_coverage_percent = min((forest_area / circle_area_km2) * 100.0, 100.0)
        urban_building_density = buildings / circle_area_km2
        return {
            "forest_coverage_percent": round(forest_coverage_percent, 2),
            "urban_building_density": round(urban_building_density, 2),
            "on_existing_building": on_existing_building
        }