"""
Membership Plans Model (MEMBERSHIP_PLANS y USER_MEMBERSHIPS)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class MembershipPlan(Base):
    """Membership plan model (MEMBERSHIP_PLANS)"""
    __tablename__ = "multiplier_plans"  # Legacy table name, will be renamed to membership_plans in future migration

    plan_id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)  # DECIMAL
    multiplier = Column(Float, nullable=False)  # DECIMAL - 1x, 2x, 3x, etc.
    duration_days = Column(Integer, nullable=False)  # Duración del plan en días
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_memberships = relationship("UserMembership", back_populates="plan")


class UserMembership(Base):
    """User membership model (USER_MEMBERSHIPS)"""
    __tablename__ = "user_memberships"  # user_plans en legacy

    membership_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("multiplier_plans.plan_id"), nullable=False)  # Legacy table name
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    payment_reference = Column(String(255), nullable=True)
    amount_paid = Column(Float, nullable=True)  # DECIMAL
    created_at = Column(Date, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memberships")
    plan = relationship("MembershipPlan", back_populates="user_memberships")

# Legacy aliases for backward compatibility
MultiplierPlan = MembershipPlan
UserPlan = UserMembership

