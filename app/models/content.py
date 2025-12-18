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
    CAROUSEL = "carousel"  # Multiple images
    AUDIO = "audio"  # Music, podcast, etc.


class ContentStatus(str, enum.Enum):
    """Enum for content status"""
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    DELETED = "deleted"


class Visibility(str, enum.Enum):
    """Enum for content visibility"""
    PUBLIC = "public"
    FOLLOWERS = "followers"  # Only followers can see
    PRIVATE = "private"


class Content(Base):
    """Published content model"""
    __tablename__ = "contents"

    content_id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(String(1000), nullable=True)  # caption
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # In seconds
    format = Column(String(50), nullable=True)
    resolution = Column(String(50), nullable=True)
    assigned_budget = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    visibility = Column(SQLEnum(Visibility), default=Visibility.PUBLIC)
    allow_comments = Column(Boolean, default=True)
    location = Column(String(255), nullable=True)  # Location text (as per spec - VARCHAR, not FK)
    is_monetizable = Column(Boolean, default=False)  # If content has active campaign
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT)
    
    # Counters (denormalized for performance)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(Date, nullable=True)

    # Relationships
    merchant = relationship("User", foreign_keys=[merchant_id], back_populates="contents")
    
    # Social relationships
    likes = relationship("Like", back_populates="content")
    comments = relationship("Comment", back_populates="content")
    post_hashtags = relationship("PostHashtag", back_populates="post")  # POST_HASHTAGS from spec
    
    # Monetization relationships
    interactions = relationship("Interaction", foreign_keys="Interaction.post_id", back_populates="content")
    
    # Multimedia files relationship
    multimedia_files = relationship("MultimediaFile", foreign_keys="MultimediaFile.post_id", back_populates="content")
    media_files = relationship("MultimediaFile", foreign_keys="MultimediaFile.post_id", back_populates="content", overlaps="multimedia_files")  # Alias
    
    # Mentions relationship
    mentions = relationship("PostMention", back_populates="post")
    
    # Audio tracks relationship
    audio_tracks = relationship("AudioTrack", foreign_keys="AudioTrack.post_id", back_populates="post")
    
    # Campaign relationships
    campaign_posts = relationship("CampaignPost", back_populates="post")
    
    # Survey relationship
    surveys = relationship("Survey", back_populates="post")

