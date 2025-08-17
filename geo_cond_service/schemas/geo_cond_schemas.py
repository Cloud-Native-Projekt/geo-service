from typing import Optional

from pydantic import BaseModel


class GeoCond(BaseModel):
    lat: float
    lon: float
    radius_km: Optional[int] = 3 
    geo_cond_id: int
    geo_cond_name: str


class GeoCondResult(BaseModel):
    near_powerline: bool
    has_substation: bool
    in_nature_reserve: bool
    forest_coverage_percent: float
    urban_building_density: float
    on_existing_building: bool