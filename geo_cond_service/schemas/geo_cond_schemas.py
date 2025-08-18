from typing import Optional

from pydantic import BaseModel


class GeoCond(BaseModel):
    lat: float
    lng: float
    radius: Optional[int] = 3000  # Default radius in meters


class GeoCondResultPower(BaseModel):
    near_powerline: bool
    has_substation: bool