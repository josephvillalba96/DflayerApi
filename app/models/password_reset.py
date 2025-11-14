"""
Password Reset Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.models.base import Base


class PasswordReset(Base):
    """Model for password reset tokens"""
    __tablename__ = "password_resets"

    reset_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    used = Column(Boolean, default=False)
    expires_at = Column(Date, nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    used_at = Column(Date, nullable=True)

    # Relationship with User
    user = relationship("User", back_populates="password_resets")

