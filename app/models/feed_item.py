"""
Feed Item Model
"""
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class FeedItem(Base):
    """User feed item model"""
    __tablename__ = "feed_items"

    feed_item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    order = Column(Integer, nullable=False)
    added_at = Column(Date, default=datetime.utcnow)
    viewed = Column(Boolean, default=False)
    viewed_at = Column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="feed_items")
    content = relationship("Content", back_populates="feed_items")
