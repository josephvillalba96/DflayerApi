"""
Action Reward Model (ACTION_REWARDS)
"""
from sqlalchemy import Column, Integer, Float, Boolean, Date, ForeignKey, Enum as SQLEnum
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


class ActionReward(Base):
    """Action reward model (ACTION_REWARDS)"""
    __tablename__ = "action_rewards"

    reward_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    base_reward_amount = Column(Float, nullable=False)  # DECIMAL - monto nivel 1
    min_view_time_seconds = Column(Integer, nullable=True)  # para acción "ver"
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    campaign = relationship("AdvertisingCampaign", back_populates="action_rewards")

