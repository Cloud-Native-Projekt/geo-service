
from geoalchemy2 import Geometry
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

    
class Substation(Base):
    __tablename__ = "substations"
    id = Column(BigInteger, primary_key=True, index=True)
    osm_id = Column(BigInteger, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)


class PowerLine(Base):
    __tablename__ = "power_lines"
    id = Column(BigInteger, primary_key=True, index=True)
    osm_id = Column(BigInteger, nullable=False)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)


class ProtectedArea(Base):
    __tablename__ = "protected_areas"
    id = Column(BigInteger, primary_key=True, index=True)
    osm_id = Column(BigInteger, nullable=False)
    designation = Column(String, nullable=True)
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)


class Forests(Base):
    __tablename__ = "forests"
    id = Column(BigInteger, primary_key=True, index=True)
    osm_id = Column(BigInteger, nullable=False)
    type = Column(String, nullable=True)
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)


class Building(Base):
    __tablename__ = "buildings"
    id = Column(BigInteger, primary_key=True, index=True)
    osm_id = Column(BigInteger, nullable=False)
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)