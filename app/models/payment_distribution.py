"""
Interaction Distribution Model (INTERACTION_DISTRIBUTIONS)
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class DistributionStatus(str, enum.Enum):
    """Enum for distribution status"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class InteractionDistribution(Base):
    """Interaction distributions model (INTERACTION_DISTRIBUTIONS)"""
    __tablename__ = "interaction_distributions"  # payment_distributions en legacy

    distribution_id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("user_interactions.interaction_id"), nullable=False)
    beneficiary_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # user_id en legacy
    level = Column(Integer, nullable=False)  # 1 a 5
    amount = Column(Float, nullable=False)  # DECIMAL
    distribution_status = Column(SQLEnum(DistributionStatus), default=DistributionStatus.PENDING)
    processed_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Legacy
    distribution_date = Column(Date, nullable=True)  # Legacy - use created_at

    # Relationships
    interaction = relationship("Interaction", back_populates="interaction_distributions")
    beneficiary_user = relationship("User", foreign_keys=[beneficiary_user_id], back_populates="interaction_distributions_received")
    
    # Legacy relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="payment_distributions")  # Legacy

# Legacy alias
PaymentDistribution = InteractionDistribution


class DistributionLevel(Base):
    """Distribution level configuration model"""
    __tablename__ = "distribution_levels"

    level_id = Column(Integer, primary_key=True, index=True)
    level_number = Column(Integer, unique=True, nullable=False)
    distribution_percentage = Column(Float, nullable=False)

