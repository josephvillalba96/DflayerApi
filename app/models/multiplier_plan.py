"""
Multiplier Plan Model
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class MultiplierPlan(Base):
    """Earnings multiplier plan model"""
    __tablename__ = "multiplier_plans"

    plan_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    multiplier_factor = Column(Float, nullable=False)

    # M:N relationship with User (through UserPlan)
    users = relationship("UserPlan", back_populates="plan")


class UserPlan(Base):
    """Intermediate table for M:N relationship between User and MultiplierPlan"""
    __tablename__ = "user_plans"

    user_plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("multiplier_plans.plan_id"), nullable=False)
    purchase_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="plans")
    plan = relationship("MultiplierPlan", back_populates="users")

