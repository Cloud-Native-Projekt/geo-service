import math
from abc import ABC, abstractmethod
from typing import Any

from geojson import FeatureCollection
from shapely.geometry import Point, shape

from geo_cond_service.schemas.geo_cond_schemas import GeoCond, GeoCondResult


class GeoCondRepositoryInterface(ABC):

	@abstractmethod
	async def get_geo_conditions(self, req: GeoCond) -> GeoCondResult:
		pass

	@abstractmethod
	async def query_power_infrastructure(self, lat: float, lon: float, radius_km: float) -> Any:
		pass

	@abstractmethod
	async def check_protected_area(self, lat: float, lon: float) -> Any:
		pass	

	@abstractmethod
	async def check_is_area_used(self, lat: float, lon: float, radius_km: float) -> Any:
		pass	