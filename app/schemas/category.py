"""
Category Schemas for Administrative Management
"""
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import BaseSchema


class CategoryCreateRequest(BaseModel):
    """Schema for creating a category (Admin only)"""
    name: str = Field(..., min_length=2, max_length=100, description="Category name (must be unique)")
    description: Optional[str] = Field(None, max_length=255, description="Category description")
    icon: Optional[str] = Field(None, max_length=100, description="Icon identifier or URL")


class CategoryUpdateRequest(BaseModel):
    """Schema for updating a category (Admin only)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=255, description="Category description")
    icon: Optional[str] = Field(None, max_length=100, description="Icon identifier or URL")


class CategoryResponse(BaseSchema):
    """Schema for category response"""
    category_id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class CategoryListResponse(BaseSchema):
    """Schema for category list response"""
    categories: list[CategoryResponse]
    total: int

