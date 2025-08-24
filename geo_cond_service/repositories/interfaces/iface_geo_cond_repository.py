from abc import ABC, abstractmethod

import geo_cond_service.schemas.geo_cond_schemas as schemas


class GeoCondRepositoryInterface(ABC):

	@abstractmethod
	async def get_power_infrastructure(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultPower:
		pass

	@abstractmethod
	async def get_protected_areas(self, lat: float, lng: int, radius: int) -> schemas.GeoCondResultProtection:
		pass	

	@abstractmethod
	async def get_buildings_in_area(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultBuildings:
		pass

	@abstractmethod
	async def get_forest_overlap(self, lat: float, lng: float, radius: int) -> schemas.GeoCondResultForest:
		pass