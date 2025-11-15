"""
Post Hashtag Model (POST_HASHTAGS)
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class PostHashtag(Base):
    """Post hashtags model (POST_HASHTAGS)"""
    __tablename__ = "post_hashtags"

    post_hashtag_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    hashtag = Column(String(100), nullable=False)  # VARCHAR - almacenado como texto
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    post = relationship("Content", back_populates="post_hashtags")

