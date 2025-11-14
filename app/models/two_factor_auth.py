"""
Two Factor Authentication Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.models.base import Base


class TwoFactorAuth(Base):
    """Model for 2FA configuration and codes"""
    __tablename__ = "two_factor_auths"

    two_factor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    enabled = Column(Boolean, default=False)
    secret_key = Column(String(255), nullable=True)  # TOTP secret key
    backup_codes = Column(String(500), nullable=True)  # JSON array of backup codes
    created_at = Column(Date, default=datetime.utcnow)
    last_used_at = Column(Date, nullable=True)

    # Relationship with User
    user = relationship("User", back_populates="two_factor_auth")


class TwoFactorCode(Base):
    """Model for temporary 2FA verification codes"""
    __tablename__ = "two_factor_codes"

    code_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    code = Column(String(10), nullable=False)  # 6-digit code
    expires_at = Column(Date, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship with User
    user = relationship("User", back_populates="two_factor_codes")

