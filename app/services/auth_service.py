"""
Servicio de Autenticación (HU001, HU002)

Este servicio maneja todas las operaciones relacionadas con la autenticación de usuarios:
- Registro de nuevos usuarios con verificación de email
- Inicio de sesión con autenticación de dos factores (2FA)
- Verificación de correo electrónico
- Restablecimiento de contraseña
- Gestión de sesiones con tokens JWT

Historia de Usuario: HU001 (Registro), HU002 (Autenticación Segura)
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
from app.services.email_service_factory import UnifiedEmailService
from app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, EmailVerificationRequest,
    TwoFactorSetupRequest, TwoFactorVerifyRequest, PasswordResetRequest,
    PasswordResetConfirmRequest
)


class AuthService:
    """
    Servicio de Autenticación
    
    Proporciona métodos para gestionar el registro, inicio de sesión, verificación de email,
    autenticación de dos factores y restablecimiento de contraseña.
    
    Características principales:
    - Registro automático con creación de sesión inmediata
    - Verificación de email obligatoria
    - Soporte para autenticación de dos factores (TOTP)
    - Restablecimiento seguro de contraseña
    - Gestión de tokens JWT para sesiones
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de autenticación
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    # Registration
    def register_user(self, user_data: UserRegisterRequest):
        """
        Registra un nuevo usuario en el sistema (HU001)
        
        Este método realiza las siguientes operaciones:
        1. Valida que el email y username no existan
        2. Crea el usuario con nivel 1 automáticamente
        3. Genera un token de verificación de email (válido por 7 días)
        4. Crea una sesión inmediata (retorna token de acceso)
        5. Envía correo de verificación automáticamente
        
        Args:
            user_data: Datos del usuario a registrar (email, password, name, username, user_type)
        
        Returns:
            Tupla con (User, verification_token, access_token)
            - User: Objeto del usuario creado
            - verification_token: Token para verificar el email
            - access_token: Token JWT para autenticación inmediata
        
        Raises:
            ValueError: Si el email o username ya existen, o si el user_type es inválido
        
        Nota: El usuario queda en sesión activa después del registro, pero debe verificar
        su email para acceder a funcionalidades completas.
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise ValueError("Username already taken")
        
        # User type is always CLIENT for new registrations
        # Only administrators can change user_type after registration
        user_type = UserType.CLIENT
        
        # Create user
        user = User(
            email=user_data.email,
            password=get_password_hash(user_data.password),
            name=user_data.name,
            username=user_data.username,
            user_type=user_type,
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
        
        # Generate access token immediately (automatic session)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email}
        )
        
        # Send verification email
        email_service = UnifiedEmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        return (user, verification_token, access_token)
    
    # Login
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario con email y contraseña
        
        Verifica las credenciales del usuario y retorna el objeto User si son válidas.
        
        Args:
            email: Correo electrónico del usuario
            password: Contraseña en texto plano (se verifica contra el hash almacenado)
        
        Returns:
            Objeto User si las credenciales son válidas, None en caso contrario
        
        Raises:
            ValueError: Si la cuenta está desactivada
        """
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
        Inicia sesión de usuario y retorna tokens (HU002)
        
        Proceso de autenticación:
        1. Verifica email y contraseña
        2. Si el usuario tiene 2FA habilitado:
           - Si no se proporciona código 2FA, retorna flag two_factor_required
           - Si se proporciona código, lo valida
        3. Genera token JWT de acceso
        
        Args:
            login_data: Datos de login (email, password, two_factor_code opcional)
        
        Returns:
            Diccionario con:
            - access_token: Token JWT para autenticación
            - token_type: Tipo de token ("bearer")
            - expires_in: Tiempo de expiración en segundos
            - user_id: ID del usuario
            - email: Email del usuario
            - user_type: Tipo de usuario
            - email_verified: Estado de verificación de email
            - two_factor_required: True si se requiere código 2FA
        
        Raises:
            ValueError: Si las credenciales son inválidas o el código 2FA es incorrecto
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
        """
        Verifica el correo electrónico del usuario con un token (HU001)
        
        Valida el token de verificación y marca el email como verificado.
        Los tokens expiran después de 7 días.
        
        Args:
            token: Token de verificación recibido por email
        
        Returns:
            True si la verificación fue exitosa, False si el token es inválido o expiró
        """
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
        """
        Reenvía el correo de verificación (HU001)
        
        Genera un nuevo token de verificación y envía un nuevo correo electrónico.
        El token anterior se invalida automáticamente.
        
        Args:
            email: Correo electrónico del usuario
        
        Returns:
            Nuevo token de verificación generado
        
        Raises:
            ValueError: Si el usuario no existe o el email ya está verificado
        """
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
        email_service = UnifiedEmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        return verification_token
    
    # Two Factor Authentication
    def setup_2fa(self, user_id: int, password: str) -> dict:
        """
        Configura la autenticación de dos factores (2FA) para un usuario (HU002)
        
        Proceso:
        1. Verifica la contraseña del usuario
        2. Genera una clave secreta única (TOTP)
        3. Genera 10 códigos de respaldo
        4. Crea un código QR para escanear con aplicación autenticadora
        5. El 2FA NO se habilita automáticamente (requiere verificación)
        
        Args:
            user_id: ID del usuario
            password: Contraseña del usuario para confirmar identidad
        
        Returns:
            Diccionario con:
            - secret_key: Clave secreta para configuración manual
            - qr_code_url: URL del código QR en formato data URI (base64)
            - backup_codes: Lista de 10 códigos de respaldo (guardar de forma segura)
        
        Raises:
            ValueError: Si el usuario no existe, la contraseña es incorrecta,
                       o el 2FA ya está habilitado
        
        Nota: El usuario debe usar verify_2fa_setup() con un código de la app
        para habilitar el 2FA después de escanear el QR.
        """
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
        """
        Verifica y habilita el 2FA usando un código de la aplicación autenticadora (HU002)
        
        Valida que el usuario haya configurado correctamente su app autenticadora
        y habilita permanentemente el 2FA para la cuenta.
        
        Args:
            user_id: ID del usuario
            code: Código de 6 dígitos generado por la aplicación autenticadora
        
        Returns:
            True si el código es válido y el 2FA fue habilitado, False en caso contrario
        """
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
        """
        Verifica un código 2FA durante el login (HU002)
        
        Acepta tanto códigos TOTP de la aplicación autenticadora como códigos de respaldo.
        Los códigos de respaldo se consumen al usarse (no se pueden reutilizar).
        
        Args:
            user_id: ID del usuario
            code: Código 2FA (TOTP de 6 dígitos o código de respaldo)
        
        Returns:
            True si el código es válido, False en caso contrario
        """
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
        """
        Deshabilita la autenticación de dos factores (HU002)
        
        Requiere tanto la contraseña como un código 2FA válido para prevenir
        deshabilitación no autorizada.
        
        Args:
            user_id: ID del usuario
            password: Contraseña del usuario
            code: Código 2FA o código de respaldo
        
        Returns:
            True si el 2FA fue deshabilitado exitosamente
        
        Raises:
            ValueError: Si el usuario no existe, la contraseña es incorrecta,
                       o el código 2FA es inválido
        """
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
        """
        Solicita el restablecimiento de contraseña (HU002)
        
        Genera un token de restablecimiento válido por 24 horas y envía un correo
        electrónico con el enlace para restablecer la contraseña.
        
        Por seguridad, este método siempre retorna un valor (incluso si el email
        no existe) para prevenir enumeración de emails.
        
        Args:
            email: Correo electrónico de la cuenta
        
        Returns:
            Token de restablecimiento si el email existe, None en caso contrario
            (pero siempre se envía el correo si el usuario existe)
        """
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
        email_service = UnifiedEmailService()
        email_service.send_password_reset_email(user.email, user.name, reset_token)
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Restablece la contraseña usando un token válido (HU002)
        
        Valida el token de restablecimiento y actualiza la contraseña del usuario.
        El token solo puede usarse una vez y expira después de 24 horas.
        
        Args:
            token: Token de restablecimiento recibido por email
            new_password: Nueva contraseña (se hashea automáticamente)
        
        Returns:
            True si la contraseña fue restablecida exitosamente, False si el token
            es inválido, expiró o ya fue usado
        """
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

