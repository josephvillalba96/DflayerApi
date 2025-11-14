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
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListResponse
)
from app.schemas.user_upgrade import (
    UserUpgradeRequest,
    UserUpgradeResponse,
    UserUpgradeStatusResponse
)
from app.schemas.admin_user import (
    ChangeUserTypeRequest,
    ChangeUserTypeResponse,
    UserUpgradeListResponse,
    RejectUpgradeRequest
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
    "CategoryCreateRequest",
    "CategoryUpdateRequest",
    "CategoryResponse",
    "CategoryListResponse",
    "UserUpgradeRequest",
    "UserUpgradeResponse",
    "UserUpgradeStatusResponse",
    "ChangeUserTypeRequest",
    "ChangeUserTypeResponse",
    "UserUpgradeListResponse",
    "RejectUpgradeRequest",
]
