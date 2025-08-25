from pydantic import BaseModel


class GeoCond(BaseModel):
    lat: float
    lng: float
    radius: int


class ResultPower(BaseModel):
    nearest_substation_distance_m: float
    nearest_powerline_distance_m: float


class ResultProtection(BaseModel):
    in_protected_area: bool


class ResultForest(BaseModel):
    forest_coverage_percent: float


class ResultBuildings(BaseModel):
    urban_building_density: float
    on_existing_building: bool
