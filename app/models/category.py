"""
Category Model
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Category(Base):
    """Content category model"""
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    icon = Column(String(100), nullable=True)

    # M:N relationship with User
    users = relationship("UserCategory", back_populates="category")

