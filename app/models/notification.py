"""
Notification Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class NotificationType(str, enum.Enum):
    """Enum for notification types"""
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    MENTION = "mention"
    TRANSACTION = "transaction"
    VOUCHER = "voucher"
    OTHER = "other"


class Notification(Base):
    """User notification model"""
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    message = Column(String(500), nullable=False)
    read = Column(Boolean, default=False)
    reference_id = Column(Integer, nullable=True)  # Varied FK depending on type
    notification_date = Column(Date, default=datetime.utcnow)

    # Relationship with User
    user = relationship("User", back_populates="notifications")

