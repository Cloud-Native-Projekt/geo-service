from pydantic import BaseModel


class GeoCond(BaseModel):
    lat: float
    lng: float
    radius: int


class ResultPower(BaseModel):
    near_powerline: bool
    has_substation: bool


class ResultProtection(BaseModel):
    in_protected_area: bool


class ResultForest(BaseModel):
    forest_coverage_percent: float


class ResultBuildings(BaseModel):
    urban_building_density: float
    on_existing_building: bool
