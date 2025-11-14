"""
Follow Model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Follow(Base):
    """User follow relationship model"""
    __tablename__ = "follows"

    follow_id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    follow_date = Column(Date, default=datetime.utcnow)

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following_sent")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="following_received")

    # Unique constraint: a user cannot follow the same user twice
    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='uq_follow'),
    )

