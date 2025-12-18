"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


# Registration Schemas
class UserRegisterRequest(BaseModel):
    """
    Schema for user registration (HU001)
    
    Nota: El user_type es siempre 'user' por defecto y no puede ser modificado
    por el usuario durante el registro. Solo los administradores pueden cambiar
    el tipo de usuario después del registro.
    
    NOTA: Solo existen 2 tipos: 'admin' y 'usuario'. Todos los usuarios tienen
    las mismas funcionalidades. is_business_account es solo visual.
    """
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number (optional but recommended)")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    # user_type removido - siempre será 'usuario' por defecto (solo admin puede cambiarlo)
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format if provided"""
        if v is not None:
            # Remove spaces, dashes, parentheses
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError('Phone number must be between 10 and 15 digits')
        return v
    
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
    """
    Schema for user login (HU002)
    
    Permite login con email o teléfono usando un solo campo 'identify'
    """
    identify: str = Field(..., description="Email address or phone number")
    password: str
    two_factor_code: Optional[str] = Field(None, max_length=6, description="2FA code if enabled")
    
    @validator('identify')
    def validate_identify(cls, v):
        """Validate that identify is not empty"""
        if not v or not v.strip():
            raise ValueError('identify field cannot be empty')
        return v.strip()


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


# SMS Verification Schemas
class SMSVerificationRequest(BaseModel):
    """Schema for SMS verification"""
    phone_number: str = Field(..., max_length=20, description="Phone number to verify")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class SMSVerificationResponse(BaseSchema):
    """Schema for SMS verification response"""
    verified: bool
    message: str


class SendSMSVerificationRequest(BaseModel):
    """Schema for sending SMS verification code"""
    phone_number: str = Field(..., max_length=20, description="Phone number to send code to")


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

