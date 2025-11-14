"""
Email Verification Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.models.base import Base


class EmailVerification(Base):
    """Model for email verification tokens"""
    __tablename__ = "email_verifications"

    verification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    verified = Column(Boolean, default=False)
    expires_at = Column(Date, nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    verified_at = Column(Date, nullable=True)

    # Relationship with User
    user = relationship("User", back_populates="email_verification")

