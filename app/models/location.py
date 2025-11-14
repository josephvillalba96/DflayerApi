"""
Location Model
"""
from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class Location(Base):
    """Geographic location model"""
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

