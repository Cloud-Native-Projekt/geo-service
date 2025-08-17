from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Reserve(Base):
    __tablename__ = "reserves"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    designation = Column(String)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))
