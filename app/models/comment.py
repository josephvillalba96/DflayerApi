"""
Comment Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Comment(Base):
    """Content comment model"""
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True)
    text = Column(String(1000), nullable=False)
    comment_date = Column(Date, default=datetime.utcnow)
    edited = Column(Boolean, default=False)
    edit_date = Column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="comments")
    content = relationship("Content", back_populates="comments")
    
    # Recursive relationship for nested replies
    parent_comment = relationship("Comment", remote_side=[comment_id], backref="replies")

