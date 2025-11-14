"""
Authentication Service
Handles user registration, login, email verification, 2FA, and password reset
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import pyotp
import qrcode
import io
import base64
import json

from app.models.user import User, UserType
from app.models.email_verification import EmailVerification
from app.models.two_factor_auth import TwoFactorAuth, TwoFactorCode
from app.models.password_reset import PasswordReset
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.services.email_service import EmailService
from app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, EmailVerificationRequest,
    TwoFactorSetupRequest, TwoFactorVerifyRequest, PasswordResetRequest,
    PasswordResetConfirmRequest
)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Registration
    def register_user(self, user_data: UserRegisterRequest):
        """
        Register a new user
        Returns: (User, verification_token)
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create user
        user = User(
            email=user_data.email,
            password=get_password_hash(user_data.password),
            name=user_data.name,
            username=user_data.username,
            user_type=UserType[user_data.user_type.upper()],
            level=1,  # HU001: Asignación automática como Usuario Nivel 1
            email_verified=False,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()  # Get user_id
        
        # Create email verification token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        email_verification = EmailVerification(
            user_id=user.user_id,
            token=verification_token,
            expires_at=expires_at
        )
        self.db.add(email_verification)
        self.db.commit()
        self.db.refresh(user)
        
        # Send verification email
        email_service = EmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        return (user, verification_token)
    
    # Login
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        return user
    
    def login_user(self, login_data: UserLoginRequest) -> dict:
        """
        Login user and return tokens
        Returns: dict with access_token and user info
        """
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if 2FA is enabled
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.user_id
        ).first()
        
        if two_factor and two_factor.enabled:
            # 2FA is enabled, verify code
            if not login_data.two_factor_code:
                return {
                    "two_factor_required": True,
                    "user_id": user.user_id
                }
            
            # Verify 2FA code
            if not self.verify_2fa_code(user.user_id, login_data.two_factor_code):
                raise ValueError("Invalid 2FA code")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user.user_id,
            "email": user.email,
            "user_type": user.user_type.value,
            "email_verified": user.email_verified,
            "two_factor_required": False
        }
    
    # Email Verification
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        verification = self.db.query(EmailVerification).filter(
            and_(
                EmailVerification.token == token,
                EmailVerification.verified == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not verification:
            return False
        
        # Mark as verified
        verification.verified = True
        verification.verified_at = datetime.utcnow()
        
        # Update user
        user = self.db.query(User).filter(User.user_id == verification.user_id).first()
        if user:
            user.email_verified = True
        
        self.db.commit()
        return True
    
    def resend_verification_email(self, email: str) -> str:
        """Resend verification email"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        
        if user.email_verified:
            raise ValueError("Email already verified")
        
        # Delete old verification
        old_verification = self.db.query(EmailVerification).filter(
            EmailVerification.user_id == user.user_id
        ).first()
        if old_verification:
            self.db.delete(old_verification)
        
        # Create new verification token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        email_verification = EmailVerification(
            user_id=user.user_id,
            token=verification_token,
            expires_at=expires_at
        )
        self.db.add(email_verification)
        self.db.commit()
        
        # Send verification email
        email_service = EmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        return verification_token
    
    # Two Factor Authentication
    def setup_2fa(self, user_id: int, password: str) -> dict:
        """Setup 2FA for user"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(password, user.password):
            raise ValueError("Invalid password")
        
        # Check if already setup
        existing = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        if existing and existing.enabled:
            raise ValueError("2FA already enabled")
        
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        
        if existing:
            existing.secret_key = secret
            existing.backup_codes = json.dumps(backup_codes)
            two_factor = existing
        else:
            two_factor = TwoFactorAuth(
                user_id=user_id,
                secret_key=secret,
                backup_codes=json.dumps(backup_codes),
                enabled=False
            )
            self.db.add(two_factor)
        
        self.db.commit()
        self.db.refresh(two_factor)
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=settings.PROJECT_NAME
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_url = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
        
        return {
            "secret_key": secret,
            "qr_code_url": qr_code_url,
            "backup_codes": backup_codes
        }
    
    def verify_2fa_setup(self, user_id: int, code: str) -> bool:
        """Verify 2FA setup with code"""
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        if not two_factor or not two_factor.secret_key:
            return False
        
        totp = pyotp.TOTP(two_factor.secret_key)
        if totp.verify(code, valid_window=1):
            two_factor.enabled = True
            self.db.commit()
            return True
        
        return False
    
    def verify_2fa_code(self, user_id: int, code: str) -> bool:
        """Verify 2FA code for login"""
        two_factor = self.db.query(TwoFactorAuth).filter(
            and_(
                TwoFactorAuth.user_id == user_id,
                TwoFactorAuth.enabled == True
            )
        ).first()
        
        if not two_factor:
            return False
        
        totp = pyotp.TOTP(two_factor.secret_key)
        
        # Check TOTP code
        if totp.verify(code, valid_window=1):
            two_factor.last_used_at = datetime.utcnow()
            self.db.commit()
            return True
        
        # Check backup codes
        if two_factor.backup_codes:
            backup_codes = json.loads(two_factor.backup_codes)
            if code in backup_codes:
                backup_codes.remove(code)
                two_factor.backup_codes = json.dumps(backup_codes)
                two_factor.last_used_at = datetime.utcnow()
                self.db.commit()
                return True
        
        return False
    
    def disable_2fa(self, user_id: int, password: str, code: str) -> bool:
        """Disable 2FA for user"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(password, user.password):
            raise ValueError("Invalid password")
        
        if not self.verify_2fa_code(user_id, code):
            raise ValueError("Invalid 2FA code")
        
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        if two_factor:
            two_factor.enabled = False
            self.db.commit()
            return True
        
        return False
    
    # Password Reset
    def request_password_reset(self, email: str) -> str:
        """Request password reset"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal if user exists
            return None
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        password_reset = PasswordReset(
            user_id=user.user_id,
            token=reset_token,
            expires_at=expires_at
        )
        self.db.add(password_reset)
        self.db.commit()
        
        # Send password reset email
        email_service = EmailService()
        email_service.send_password_reset_email(user.email, user.name, reset_token)
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        reset = self.db.query(PasswordReset).filter(
            and_(
                PasswordReset.token == token,
                PasswordReset.used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not reset:
            return False
        
        # Update password
        user = self.db.query(User).filter(User.user_id == reset.user_id).first()
        if user:
            user.password = get_password_hash(new_password)
        
        # Mark token as used
        reset.used = True
        reset.used_at = datetime.utcnow()
        
        self.db.commit()
        return True

