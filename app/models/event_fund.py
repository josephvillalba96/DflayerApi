"""
Event Fund Model
"""
from sqlalchemy import Column, Integer, Float, Date
from datetime import datetime
from app.models.base import Base


class EventFund(Base):
    """Special events fund model"""
    __tablename__ = "event_funds"

    fund_id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

