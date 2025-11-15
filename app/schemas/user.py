"""
User Schemas (HU004)
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime
from app.schemas.base import BaseSchema


class ProfileUpdateRequest(BaseModel):
    """Schema for updating user profile (HU004)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre completo del usuario")
    biography: Optional[str] = Field(None, max_length=500, description="Biografía del usuario")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    location_id: Optional[int] = Field(None, description="ID de ubicación")


class ProfilePictureUpdateRequest(BaseModel):
    """Schema for updating profile picture (HU004)"""
    profile_picture_url: str = Field(..., max_length=500, description="URL de la foto de perfil")


class CoverPictureUpdateRequest(BaseModel):
    """Schema for updating cover picture (HU004)"""
    cover_picture_url: str = Field(..., max_length=500, description="URL de la foto de portada")


class UserProfileResponse(BaseSchema):
    """Schema for user profile response (HU004)"""
    user_id: int
    name: str
    username: str
    email: str
    biography: Optional[str] = None
    profile_picture: Optional[str] = None
    cover_picture: Optional[str] = None
    birth_date: Optional[date] = None
    location_id: Optional[int] = None
    level: int
    verified: bool
    following_count: int
    followers_count: int
    registration_date: datetime
    interest_categories: List[str] = []


class InterestCategoryRequest(BaseModel):
    """Schema for adding interest category (HU004)"""
    category_id: int = Field(..., description="ID de la categoría de interés")


class InterestCategoryResponse(BaseSchema):
    """Schema for interest category response (HU004)"""
    category_id: int
    category_name: str
    added_at: datetime


class InterestCategoriesListResponse(BaseSchema):
    """Schema for list of interest categories (HU004)"""
    categories: List[InterestCategoryResponse]
    total: int

