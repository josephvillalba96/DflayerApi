"""
Schemas package
"""
from app.schemas.base import BaseSchema, MessageResponse, HealthResponse
from app.schemas.auth import (
    UserRegisterRequest, UserRegisterResponse,
    UserLoginRequest, TokenResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    ResendVerificationRequest,
    TwoFactorSetupRequest, TwoFactorSetupResponse,
    TwoFactorVerifyRequest, TwoFactorDisableRequest,
    PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetResponse,
    UserInfo
)
from app.schemas.feed import FeedRequest, FeedResponse, FeedItemResponse
# Category schemas removed - Category model not in spec
from app.schemas.admin_user import (
    ChangeUserTypeRequest,
    ChangeUserTypeResponse,
    PromoteRequest
)
from app.schemas.user import (
    ProfileUpdateRequest,
    ProfilePictureUpdateRequest,
    CoverPictureUpdateRequest,
    UserProfileResponse,
    InterestCategoryRequest,
    InterestCategoryResponse,
    InterestCategoriesListResponse
)

__all__ = [
    "BaseSchema",
    "MessageResponse",
    "HealthResponse",
    "UserRegisterRequest",
    "UserRegisterResponse",
    "UserLoginRequest",
    "TokenResponse",
    "EmailVerificationRequest",
    "EmailVerificationResponse",
    "ResendVerificationRequest",
    "TwoFactorSetupRequest",
    "TwoFactorSetupResponse",
    "TwoFactorVerifyRequest",
    "TwoFactorDisableRequest",
    "PasswordResetRequest",
    "PasswordResetConfirmRequest",
    "PasswordResetResponse",
    "UserInfo",
    "FeedRequest",
    "FeedResponse",
    "FeedItemResponse",
    "ChangeUserTypeRequest",
    "ChangeUserTypeResponse",
    "PromoteRequest",
    "ProfileUpdateRequest",
    "ProfilePictureUpdateRequest",
    "CoverPictureUpdateRequest",
    "UserProfileResponse",
    "InterestCategoryRequest",
    "InterestCategoryResponse",
    "InterestCategoriesListResponse",
]
