"""
Monetizable Action Model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base


class ActionType(str, enum.Enum):
    """Enum for monetizable action types"""
    SHARE = "share"
    RESPOND = "respond"
    VIEW = "view"
    SPONSOR = "sponsor"


class MonetizableAction(Base):
    """Model for actions that can be monetized"""
    __tablename__ = "monetizable_actions"

    action_id = Column(Integer, primary_key=True, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    base_value = Column(Float, nullable=False, default=0.0)
    multiplier = Column(Float, default=1.0)

    # Relationship with Interactions
    interactions = relationship("Interaction", back_populates="action")

