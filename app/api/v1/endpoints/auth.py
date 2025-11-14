"""
Authentication Endpoints
Handles registration, login, email verification, 2FA, and password reset
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.db.base import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegisterRequest, UserRegisterResponse,
    UserLoginRequest, TokenResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    ResendVerificationRequest,
    TwoFactorSetupRequest, TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorDisableRequest,
    PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetResponse,
    UserInfo
)
from app.core.security import decode_access_token
from app.models.user import User
from app.models.two_factor_auth import TwoFactorAuth

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


# Registration Endpoints
@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (HU001)
    
    - **email**: User email (must be unique)
    - **password**: Password (min 8 chars, must contain uppercase, lowercase, and digit)
    - **name**: Full name
    - **username**: Username (min 3 chars, alphanumeric and underscore only)
    - **user_type**: Type of user (client, merchant, affiliate)
    
    Automatically assigns user as Level 1 and sends verification email.
    """
    auth_service = AuthService(db)
    
    try:
        user, verification_token = auth_service.register_user(user_data)
        
        # Email sent automatically via AuthService
        
        return UserRegisterResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            username=user.username,
            user_type=user.user_type.value,
            level=user.level,
            email_verified=user.email_verified,
            message="Registration successful. Please verify your email."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Login Endpoints
@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user (HU002)
    
    - **email**: User email
    - **password**: User password
    - **two_factor_code**: 2FA code (required if 2FA is enabled)
    
    Returns access token if authentication is successful.
    If 2FA is enabled and code is not provided, returns two_factor_required flag.
    """
    auth_service = AuthService(db)
    
    try:
        result = auth_service.login_user(login_data)
        
        # Check if 2FA is required
        if result.get("two_factor_required"):
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="2FA code required",
                headers={"X-2FA-Required": "true"}
            )
        
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# Email Verification Endpoints
@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token (HU001)
    
    - **token**: Verification token sent to email
    
    Marks email as verified if token is valid.
    """
    auth_service = AuthService(db)
    
    verified = auth_service.verify_email(verification_data.token)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return EmailVerificationResponse(
        verified=True,
        message="Email verified successfully"
    )


@router.post("/resend-verification")
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification email (HU001)
    
    - **email**: User email
    
    Sends a new verification email to the user.
    """
    auth_service = AuthService(db)
    
    try:
        token = auth_service.resend_verification_email(request.email)
        
        # Email sent automatically via AuthService
        
        return {
            "message": "Verification email sent"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Two Factor Authentication Endpoints
@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup Two Factor Authentication (HU002)
    
    - **password**: User password for confirmation
    
    Generates secret key, QR code, and backup codes.
    User must verify with a code to enable 2FA.
    """
    auth_service = AuthService(db)
    
    try:
        result = auth_service.setup_2fa(current_user.user_id, request.password)
        
        return TwoFactorSetupResponse(
            secret_key=result["secret_key"],
            qr_code_url=result["qr_code_url"],
            backup_codes=result["backup_codes"],
            message="Scan QR code with authenticator app and verify with code"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/2fa/verify")
async def verify_2fa_setup(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify and enable 2FA setup (HU002)
    
    - **code**: 6-digit code from authenticator app
    
    Enables 2FA after successful verification.
    """
    auth_service = AuthService(db)
    
    verified = auth_service.verify_2fa_setup(current_user.user_id, request.code)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    
    return {
        "message": "2FA enabled successfully",
        "enabled": True
    }


@router.post("/2fa/disable")
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable Two Factor Authentication (HU002)
    
    - **password**: User password
    - **code**: 2FA code or backup code
    
    Disables 2FA for the user.
    """
    auth_service = AuthService(db)
    
    try:
        disabled = auth_service.disable_2fa(
            current_user.user_id,
            request.password,
            request.code
        )
        
        if not disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disable 2FA"
            )
        
        return {
            "message": "2FA disabled successfully",
            "enabled": False
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/2fa/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 2FA status for current user"""
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.user_id
    ).first()
    
    return {
        "enabled": two_factor.enabled if two_factor else False,
        "setup": two_factor is not None
    }


# Password Reset Endpoints
@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset (HU002)
    
    - **email**: User email
    
    Sends password reset email if user exists.
    """
    auth_service = AuthService(db)
    
    token = auth_service.request_password_reset(request.email)
    
    # Email sent automatically via AuthService
    # Always return success to prevent email enumeration
    
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent",
        success=True
    )


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset (HU002)
    
    - **token**: Password reset token
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, and digit)
    
    Resets password if token is valid.
    """
    auth_service = AuthService(db)
    
    success = auth_service.reset_password(request.token, request.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return PasswordResetResponse(
        message="Password reset successfully",
        success=True
    )


# User Info Endpoint
@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user information"""
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.user_id
    ).first()
    
    return UserInfo(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        username=current_user.username,
        user_type=current_user.user_type.value,
        level=current_user.level,
        email_verified=current_user.email_verified,
        two_factor_enabled=two_factor.enabled if two_factor else False,
        is_active=current_user.is_active,
        registration_date=current_user.registration_date
    )

