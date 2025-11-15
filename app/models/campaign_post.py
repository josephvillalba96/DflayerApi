"""
Campaign Post Model (CAMPAIGN_POSTS)
"""
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class CampaignPost(Base):
    """Campaign post model (CAMPAIGN_POSTS)"""
    __tablename__ = "campaign_posts"

    campaign_post_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    linked_at = Column(Date, default=datetime.utcnow)

    # Relationships
    campaign = relationship("AdvertisingCampaign", back_populates="campaign_posts")
    post = relationship("Content", back_populates="campaign_posts")

