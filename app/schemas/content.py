"""
Content Schemas (HU006)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class ContentCreateRequest(BaseModel):
    """Schema for creating content (HU006)"""
    title: Optional[str] = Field(None, max_length=200, description="Content title")
    description: Optional[str] = Field(None, max_length=1000, description="Content description")
    content_type: str = Field(..., pattern="^(video|image|text|audio)$", description="Type of content")
    url: Optional[str] = Field(None, max_length=500, description="Content URL (if already uploaded)")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="Thumbnail URL")
    visibility: str = Field(default="public", pattern="^(public|private)$", description="Content visibility")
    allow_comments: bool = Field(default=True, description="Allow comments on content")
    location_id: Optional[int] = Field(None, description="Location ID for geotagging")
    category_ids: Optional[List[int]] = Field(default=[], description="Category IDs for content categorization")
    hashtags: Optional[List[str]] = Field(default=[], description="Hashtags for content")
    scheduled_publish_at: Optional[datetime] = Field(None, description="Schedule publication date/time")
    target_audience: Optional[str] = Field(None, max_length=500, description="Target audience description")
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        """Validate hashtags format"""
        if v:
            for tag in v:
                if not tag.startswith('#'):
                    raise ValueError(f'Hashtag "{tag}" must start with #')
                if len(tag) < 2 or len(tag) > 50:
                    raise ValueError(f'Hashtag "{tag}" must be between 2 and 50 characters')
        return v


class ContentUpdateRequest(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    visibility: Optional[str] = Field(None, pattern="^(public|private)$")
    allow_comments: Optional[bool] = None
    active: Optional[bool] = None


class ContentResponse(BaseSchema):
    """Schema for content response"""
    content_id: int
    merchant_id: int
    merchant_name: Optional[str] = None
    content_type: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    format: Optional[str] = None
    resolution: Optional[str] = None
    visibility: str
    allow_comments: bool
    active: bool
    created_at: datetime
    published_at: Optional[datetime] = None
    location_id: Optional[int] = None
    categories: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []


class ContentListResponse(BaseSchema):
    """Schema for content list response"""
    contents: List[ContentResponse]
    total: int
    page: int
    page_size: int


