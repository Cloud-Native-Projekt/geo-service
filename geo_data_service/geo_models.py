
from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

    
class Substation(Base):
    __tablename__ = "substations"
    id = Column(BigInteger, primary_key=True, index=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)


class PowerLine(Base):
    __tablename__ = "power_lines"
    id = Column(BigInteger, primary_key=True, index=True)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)


class ProtectedArea(Base):
    __tablename__ = "protected_areas"
    id = Column(BigInteger, primary_key=True, index=True)
    designation = Column(String, nullable=True)
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)


class ForestCover(Base):
    __tablename__ = "forest_cover"
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(String, nullable=True)  # z.B. "deciduous", "coniferous"
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)


class Building(Base):
    __tablename__ = "buildings"
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(String, nullable=True)  # "residential", "commercial", etc.
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)