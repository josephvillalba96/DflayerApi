"""
Referral Network Model
5-level referral network system
"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import sqlalchemy as sa
from app.models.base import Base


class ReferralNetwork(Base):
    """Referral network model - 5 levels"""
    __tablename__ = "referral_network"

    referral_id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # quien refiere
    referred_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # quien fue referido
    level = Column(Integer, nullable=False)  # 1 a 5
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_sent")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")

    # Unique constraint: a user can only be referred once by the same referrer at the same level
    __table_args__ = (
        sa.UniqueConstraint('referrer_id', 'referred_id', 'level', name='uq_referral_level'),
        {'sqlite_autoincrement': True},
    )

