"""
Hashtag Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Hashtag(Base):
    """Hashtag model"""
    __tablename__ = "hashtags"

    hashtag_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    usage_count = Column(Integer, default=0)
    trending = Column(Boolean, default=False)
    created_at = Column(Date, default=datetime.utcnow)

    # M:N relationship with Content
    contents = relationship("ContentHashtag", back_populates="hashtag")


class ContentHashtag(Base):
    """Intermediate table for M:N relationship between Content and Hashtag"""
    __tablename__ = "content_hashtags"

    content_hashtag_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.hashtag_id"), nullable=False)

    # Relationships
    content = relationship("Content", back_populates="hashtags")
    hashtag = relationship("Hashtag", back_populates="contents")

    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
