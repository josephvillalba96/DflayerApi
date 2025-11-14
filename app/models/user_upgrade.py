"""
User Upgrade Request Model
Tracks user requests to upgrade from client to merchant/affiliate
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class UpgradeRequestStatus(str, enum.Enum):
    """Enum for upgrade request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserUpgradeRequest(Base):
    """User upgrade request model"""
    __tablename__ = "user_upgrade_requests"

    upgrade_request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    current_user_type = Column(String(50), nullable=False)
    requested_user_type = Column(String(50), nullable=False)  # merchant or affiliate
    status = Column(SQLEnum(UpgradeRequestStatus), default=UpgradeRequestStatus.PENDING)
    reason = Column(String(500), nullable=True)
    business_name = Column(String(200), nullable=True)
    business_description = Column(String(1000), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Admin who reviewed
    reviewed_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

