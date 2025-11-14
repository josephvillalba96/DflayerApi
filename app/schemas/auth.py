"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


# Registration Schemas
class UserRegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    user_type: str = Field(default="client", pattern="^(client|merchant|affiliate)$")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserRegisterResponse(BaseSchema):
    """Schema for registration response"""
    user_id: int
    email: str
    name: str
    username: str
    user_type: str
    level: int
    email_verified: bool
    message: str


# Login Schemas
class UserLoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = Field(None, max_length=6, description="2FA code if enabled")


class TokenResponse(BaseSchema):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    user_type: str
    email_verified: bool
    two_factor_required: bool = False


# Email Verification Schemas
class EmailVerificationRequest(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., description="Verification token sent to email")


class EmailVerificationResponse(BaseSchema):
    """Schema for email verification response"""
    verified: bool
    message: str


class ResendVerificationRequest(BaseModel):
    """Schema for resending verification email"""
    email: EmailStr


# Two Factor Authentication Schemas
class TwoFactorSetupRequest(BaseModel):
    """Schema for 2FA setup request"""
    password: str = Field(..., description="User password confirmation")


class TwoFactorSetupResponse(BaseSchema):
    """Schema for 2FA setup response"""
    secret_key: str
    qr_code_url: str
    backup_codes: list[str]
    message: str


class TwoFactorVerifyRequest(BaseModel):
    """Schema for 2FA verification"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit 2FA code")


class TwoFactorDisableRequest(BaseModel):
    """Schema for disabling 2FA"""
    password: str
    code: str = Field(..., min_length=6, max_length=6)


# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class PasswordResetResponse(BaseSchema):
    """Schema for password reset response"""
    message: str
    success: bool


# User Info Schemas
class UserInfo(BaseSchema):
    """Schema for user information"""
    user_id: int
    email: str
    name: str
    username: str
    user_type: str
    level: int
    email_verified: bool
    two_factor_enabled: bool
    is_active: bool
    registration_date: datetime

