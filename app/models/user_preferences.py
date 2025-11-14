"""
User Preferences Model
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class UserPreferences(Base):
    """User preferences and configuration model"""
    __tablename__ = "user_preferences"

    preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    algorithm_preference = Column(String(50), default="recommended")  # recommended, following, trending
    push_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)

    # 1:1 relationship with User
    user = relationship("User", back_populates="preferences")


class UserCategory(Base):
    """Intermediate table for M:N relationship between User and Category (interests)"""
    __tablename__ = "user_categories"

    user_category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="interest_categories")
    category = relationship("Category", back_populates="users")

    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

