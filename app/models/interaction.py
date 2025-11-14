"""
Interaction Model
"""
from sqlalchemy import Column, Integer, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Interaction(Base):
    """Model for monetizable user interactions with content"""
    __tablename__ = "interactions"

    interaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    action_id = Column(Integer, ForeignKey("monetizable_actions.action_id"), nullable=False)
    amount_paid = Column(Float, default=0.0)
    interaction_date = Column(Date, default=datetime.utcnow)
    validated = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
    action = relationship("MonetizableAction", back_populates="interactions")
    
    # Relationship with payment distributions
    payment_distributions = relationship("PaymentDistribution", back_populates="interaction")

