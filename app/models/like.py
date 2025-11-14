"""
Like Model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Like(Base):
    """Content like model"""
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    like_date = Column(Date, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="likes")
    content = relationship("Content", back_populates="likes")

    # Unique constraint: a user cannot like the same content twice
    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='uq_like'),
    )
