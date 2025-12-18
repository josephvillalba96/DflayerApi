"""
User Interaction Model (USER_INTERACTIONS)
"""
from sqlalchemy import Column, Integer, Float, Boolean, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class ActionType(str, enum.Enum):
    """Enum for action types"""
    SHARE = "share"
    RESPOND = "respond"
    VIEW = "view"
    SPONSOR = "sponsor"


class ValidationStatus(str, enum.Enum):
    """Enum for validation status"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class Interaction(Base):
    """User interactions model (USER_INTERACTIONS)"""
    __tablename__ = "user_interactions"  # interactions en legacy

    interaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)  # content_id en legacy
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=True)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    reward_amount = Column(Float, nullable=False)  # DECIMAL
    interaction_timestamp = Column(Date, default=datetime.utcnow)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)
    interaction_metadata = Column(Text, nullable=True)  # JSON con datos adicionales (metadata es palabra reservada)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=True)  # Legacy
    amount_paid = Column(Float, default=0.0)  # Legacy - use reward_amount
    interaction_date = Column(Date, nullable=True)  # Legacy - use interaction_timestamp
    validated = Column(Boolean, default=False)  # Legacy - use validation_status

    # Relationships
    user = relationship("User", back_populates="interactions")
    content = relationship("Content", foreign_keys=[post_id], back_populates="interactions")
    campaign = relationship("AdvertisingCampaign", back_populates="interactions")
    
    # Relationship with payment distributions
    interaction_distributions = relationship("InteractionDistribution", back_populates="interaction")
    payment_distributions = relationship("InteractionDistribution", foreign_keys="InteractionDistribution.interaction_id", back_populates="interaction", overlaps="interaction_distributions")  # Legacy: PaymentDistribution is alias

