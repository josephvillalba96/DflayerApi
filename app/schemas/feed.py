"""
Feed Schemas (HU007)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema
from app.schemas.content import ContentResponse


class FeedRequest(BaseModel):
    """Schema for feed request with filters"""
    skip: int = Field(default=0, ge=0, description="Number of records to skip for pagination")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of records to return (1-100)")
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    location_id: Optional[int] = Field(None, description="Filter by location ID")
    algorithm: Optional[str] = Field(
        default="recommended",
        pattern="^(recommended|following|trending|recent)$",
        description="Feed algorithm: recommended (by interests), following (from followed users), trending (by engagement), recent (newest first)"
    )


class FeedItemResponse(BaseSchema):
    """Schema for feed item response"""
    content: ContentResponse
    relevance_score: Optional[float] = Field(None, description="Relevance score for recommended algorithm")
    is_following_creator: Optional[bool] = Field(None, description="Whether user is following the content creator")
    engagement_score: Optional[float] = Field(None, description="Engagement score (for trending algorithm)")


class FeedResponse(BaseSchema):
    """Schema for feed response"""
    items: List[FeedItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
    algorithm_used: str

