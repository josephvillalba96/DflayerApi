"""
Content Model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class ContentType(str, enum.Enum):
    """Enum for content types"""
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"  # Music, podcast, etc.


class Visibility(str, enum.Enum):
    """Enum for content visibility"""
    PUBLIC = "public"
    PRIVATE = "private"


class Content(Base):
    """Published content model"""
    __tablename__ = "contents"

    content_id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # In seconds
    format = Column(String(50), nullable=True)
    resolution = Column(String(50), nullable=True)
    assigned_budget = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    visibility = Column(SQLEnum(Visibility), default=Visibility.PUBLIC)
    allow_comments = Column(Boolean, default=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=True)
    created_at = Column(Date, default=datetime.utcnow)
    published_at = Column(Date, nullable=True)

    # Relationships
    merchant = relationship("User", foreign_keys=[merchant_id], back_populates="contents")
    location = relationship("Location", foreign_keys=[location_id])
    
    # Social relationships
    likes = relationship("Like", back_populates="content")
    comments = relationship("Comment", back_populates="content")
    hashtags = relationship("ContentHashtag", back_populates="content")
    
    # Monetization relationships
    interactions = relationship("Interaction", back_populates="content")
    
    # Feed and metrics relationships
    feed_items = relationship("FeedItem", back_populates="content")
    metrics = relationship("ContentMetrics", back_populates="content", uselist=False)
    
    # Multimedia files relationship
    multimedia_files = relationship("MultimediaFile", back_populates="content")

