"""
Campaign Segmentation Model (CAMPAIGN_SEGMENTATION)
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class Gender(str, enum.Enum):
    """Enum for gender"""
    ALL = "all"
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CampaignSegmentation(Base):
    """Campaign segmentation model (CAMPAIGN_SEGMENTATION)"""
    __tablename__ = "campaign_segmentation"

    segmentation_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), unique=True, nullable=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    gender = Column(SQLEnum(Gender), default=Gender.ALL)
    countries = Column(Text, nullable=True)  # JSON array
    cities = Column(Text, nullable=True)  # JSON array
    interests = Column(Text, nullable=True)  # JSON array
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    campaign = relationship("AdvertisingCampaign", back_populates="segmentation")

