"""
Post Mention Model
User mentions in content posts (@username)
"""
from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class PostMention(Base):
    """Post mention model"""
    __tablename__ = "post_mentions"

    mention_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    mentioned_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationships
    post = relationship("Content", back_populates="mentions")
    mentioned_user = relationship("User", back_populates="mentions_received")

