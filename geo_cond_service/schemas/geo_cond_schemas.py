from typing import Optional

from pydantic import BaseModel


class GeoCond(BaseModel):
    lat: float
    lng: float
    radius: Optional[int] = 3000  # Default radius in meters


class GeoCondResultPower(BaseModel):
    near_powerline: bool
    has_substation: bool
    
class GeoCondResultProtection(BaseModel):
    in_protected_area: bool
    
class GeoCondResultForest(BaseModel):
    forest_coverage_percent: float

class GeoCondResultBuildings(BaseModel):
    urban_building_density: float
    on_existing_building: bool