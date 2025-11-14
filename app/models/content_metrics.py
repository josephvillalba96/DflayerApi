"""
Content Metrics Model
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class ContentMetrics(Base):
    """Content engagement metrics model"""
    __tablename__ = "content_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.content_id"), unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    average_view_duration = Column(Float, default=0.0)  # In seconds
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 1:1 relationship with Content
    content = relationship("Content", back_populates="metrics")

