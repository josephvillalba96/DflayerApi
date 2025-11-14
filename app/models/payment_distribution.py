"""
Payment Distribution Model
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class PaymentDistribution(Base):
    """Multi-level payment distribution model"""
    __tablename__ = "payment_distributions"

    distribution_id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.interaction_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    level = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    distribution_date = Column(Date, default=datetime.utcnow)

    # Relationships
    interaction = relationship("Interaction", back_populates="payment_distributions")
    user = relationship("User", back_populates="payment_distributions")


class DistributionLevel(Base):
    """Distribution level configuration model"""
    __tablename__ = "distribution_levels"

    level_id = Column(Integer, primary_key=True, index=True)
    level_number = Column(Integer, unique=True, nullable=False)
    distribution_percentage = Column(Float, nullable=False)

