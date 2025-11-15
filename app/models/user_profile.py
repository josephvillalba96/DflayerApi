"""
User Profile Model (HU004)
Extended profiles for personal and business users
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class ProfileType(str, enum.Enum):
    """Enum for profile types"""
    PERSONAL = "personal"
    BUSINESS = "business"


class UserProfile(Base):
    """Extended user profile model"""
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    profile_type = Column(SQLEnum(ProfileType), nullable=False, default=ProfileType.PERSONAL)
    
    # Business profile fields
    business_name = Column(String(200), nullable=True)
    business_category = Column(String(100), nullable=True)
    website_url = Column(String(500), nullable=True)
    
    # Address fields
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="profile", uselist=False)

