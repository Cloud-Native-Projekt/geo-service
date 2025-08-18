import math
from abc import ABC, abstractmethod
from typing import Any

from geojson import FeatureCollection
from shapely.geometry import Point, shape

from geo_cond_service.schemas.geo_cond_schemas import GeoCond, GeoCondResultPower


class GeoCondRepositoryInterface(ABC):

	@abstractmethod
	async def query_power_infrastructure(self, lat: float, lng: float, radius: int) -> GeoCondResultPower:
		pass

	@abstractmethod
	async def check_protected_area(self, lat: float, lng: int) -> Any:
		pass	

	@abstractmethod
	async def check_is_area_used(self, lat: float, lng: float, radius: int) -> Any:
		pass	