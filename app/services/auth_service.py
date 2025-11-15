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
from app.models.password_reset import PasswordReset
from app.models.two_factor_auth import TwoFactorAuth
from app.models.sms_verification import SMSVerification
from app.services.sms_service import SMSService
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
        
        # Check if phone_number already exists (if provided)
        if user_data.phone_number:
            existing_phone = self.db.query(User).filter(User.phone_number == user_data.phone_number).first()
            if existing_phone:
                raise ValueError("Phone number already registered")
        
        # User type is always USER (usuario) for new registrations
        # Only admin can change user_type after registration
        user_type = UserType.USER
        
        # Create user
        user = User(
            email=user_data.email,
            phone_number=user_data.phone_number,
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
        
        # Generate verification token for email (HU001: valid for 10 minutes)
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Store verification token in database
        email_verification = EmailVerification(
            user_id=user.user_id,
            token=verification_token,
            expires_at=expires_at,
            verified=False
        )
        self.db.add(email_verification)
        self.db.flush()
        
        # Generate access token immediately (automatic session)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email}
        )
        
        # Send verification email
        email_service = UnifiedEmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        # Send SMS verification code if phone_number provided (HU001)
        # Nota: Si Twilio no está configurado, solo se guarda el código pero no se envía SMS real
        # El registro continúa normalmente usando solo email
        sms_code = None
        if user_data.phone_number:
            try:
                sms_service = SMSService()
                sms_code = sms_service.generate_code()
                expires_at_sms = datetime.utcnow() + timedelta(minutes=10)
                
                sms_verification = SMSVerification(
                    user_id=user.user_id,
                    phone_number=user_data.phone_number,
                    code=sms_code,
                    expires_at=expires_at_sms,
                    verified=False
                )
                self.db.add(sms_verification)
                self.db.flush()
                
                # Send SMS (no falla si Twilio no está configurado, solo loguea)
                sms_service.send_verification_code(user_data.phone_number, sms_code)
            except Exception as e:
                # Si hay algún error con SMS, no bloquear el registro
                # El usuario puede verificar por email mientras tanto
                print(f"[WARNING] Error al procesar SMS durante registro (no crítico): {str(e)}")
                print(f"[INFO] El registro se completó exitosamente. El usuario puede verificar por email.")
        
        return (user, verification_token, access_token)
    
    # Login
    def authenticate_user(self, email: Optional[str] = None, phone_number: Optional[str] = None, password: str = "") -> Optional[User]:
        """
        Autentica un usuario con email/teléfono y contraseña (HU002)
        
        Verifica las credenciales del usuario y retorna el objeto User si son válidas.
        Permite autenticación con email o teléfono.
        
        Args:
            email: Correo electrónico del usuario (opcional si se proporciona phone_number)
            phone_number: Número de teléfono del usuario (opcional si se proporciona email)
            password: Contraseña en texto plano (se verifica contra el hash almacenado)
        
        Returns:
            Objeto User si las credenciales son válidas, None en caso contrario
        
        Raises:
            ValueError: Si la cuenta está desactivada o si no se proporciona email ni teléfono
        """
        if not email and not phone_number:
            raise ValueError("Either email or phone_number must be provided")
        
        # Search by email or phone_number
        if email:
            user = self.db.query(User).filter(User.email == email).first()
        else:
            user = self.db.query(User).filter(User.phone_number == phone_number).first()
        
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
        user = self.authenticate_user(
            email=login_data.email,
            phone_number=login_data.phone_number,
            password=login_data.password
        )
        if not user:
            raise ValueError("Invalid credentials")
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            # If 2FA is enabled but no code provided, require it
            if not login_data.two_factor_code:
                return {
                    "access_token": "",
                    "token_type": "bearer",
                    "expires_in": 0,
                    "user_id": user.user_id,
                    "email": user.email,
                    "user_type": user.user_type.value,
                    "email_verified": user.email_verified,
                    "two_factor_required": True
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
    
    # Email Verification (HU001)
    def verify_email(self, token: str) -> bool:
        """
        Verifica el correo electrónico del usuario con un token (HU001)
        
        Valida el token de verificación y marca el email como verificado.
        El token debe ser válido y no expirado (10 minutos).
        
        Args:
            token: Token de verificación recibido por email
        
        Returns:
            True si la verificación fue exitosa
        
        Raises:
            ValueError: Si el token es inválido, expirado o ya fue usado
        """
        verification = self.db.query(EmailVerification).filter(
            EmailVerification.token == token
        ).first()
        
        if not verification:
            raise ValueError("Invalid verification token")
        
        if verification.is_expired():
            raise ValueError("Verification token has expired")
        
        if verification.verified:
            raise ValueError("Email already verified")
        
        # Mark as verified
        verification.verified = True
        verification.verified_at = datetime.utcnow()
        
        # Update user email_verified status
        user = self.db.query(User).filter(User.user_id == verification.user_id).first()
        if user:
            user.email_verified = True
        
        self.db.commit()
        return True
    
    def resend_verification_email(self, email: str) -> str:
        """
        Reenvía el correo de verificación (HU001)
        
        Genera un nuevo token de verificación y envía el email.
        Invalida el token anterior si existe.
        
        Args:
            email: Email del usuario
        
        Returns:
            Nuevo token de verificación
        
        Raises:
            ValueError: Si el usuario no existe o el email ya está verificado
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        
        if user.email_verified:
            raise ValueError("Email already verified")
        
        # Invalidate old verification tokens
        old_verifications = self.db.query(EmailVerification).filter(
            EmailVerification.user_id == user.user_id,
            EmailVerification.verified == False
        ).all()
        for old_ver in old_verifications:
            self.db.delete(old_ver)
        
        # Generate new token (valid for 10 minutes)
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        email_verification = EmailVerification(
            user_id=user.user_id,
            token=verification_token,
            expires_at=expires_at,
            verified=False
        )
        self.db.add(email_verification)
        self.db.commit()
        
        # Send verification email
        email_service = UnifiedEmailService()
        email_service.send_verification_email(user.email, user.name, verification_token)
        
        return verification_token
    
    # SMS Verification (HU001)
    def send_sms_verification_code(self, user_id: int, phone_number: str) -> str:
        """
        Envía un código de verificación por SMS (HU001)
        
        Genera un código de 6 dígitos y lo envía por SMS al número proporcionado.
        El código es válido por 10 minutos.
        
        Args:
            user_id: ID del usuario
            phone_number: Número de teléfono donde enviar el código
        
        Returns:
            Código de verificación generado
        
        Raises:
            ValueError: Si el usuario no existe
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Invalidate old SMS verification codes
        old_verifications = self.db.query(SMSVerification).filter(
            SMSVerification.user_id == user_id,
            SMSVerification.phone_number == phone_number,
            SMSVerification.verified == False
        ).all()
        for old_ver in old_verifications:
            self.db.delete(old_ver)
        
        # Generate new code (valid for 10 minutes)
        sms_service = SMSService()
        code = sms_service.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        sms_verification = SMSVerification(
            user_id=user_id,
            phone_number=phone_number,
            code=code,
            expires_at=expires_at,
            verified=False
        )
        self.db.add(sms_verification)
        self.db.commit()
        
        # Send SMS (no falla si Twilio no está configurado)
        try:
            sms_service.send_verification_code(phone_number, code)
        except Exception as e:
            # Si falla el envío, no lanzar excepción, solo loguear
            print(f"[WARNING] Error al enviar SMS (no crítico): {str(e)}")
            print(f"[INFO] El código se generó y guardó correctamente. Verifica los logs para ver el código.")
        
        return code
    
    def verify_sms_code(self, user_id: int, phone_number: str, code: str) -> bool:
        """
        Verifica un código SMS (HU001)
        
        Valida el código de verificación SMS y marca el teléfono como verificado.
        El código debe ser válido y no expirado (10 minutos).
        Máximo 5 intentos de verificación.
        
        Args:
            user_id: ID del usuario
            phone_number: Número de teléfono a verificar
            code: Código de 6 dígitos recibido por SMS
        
        Returns:
            True si la verificación fue exitosa
        
        Raises:
            ValueError: Si el código es inválido, expirado o se excedieron los intentos
        """
        verification = self.db.query(SMSVerification).filter(
            SMSVerification.user_id == user_id,
            SMSVerification.phone_number == phone_number,
            SMSVerification.verified == False
        ).order_by(SMSVerification.created_at.desc()).first()
        
        if not verification:
            raise ValueError("No verification code found for this phone number")
        
        if verification.is_expired():
            raise ValueError("Verification code has expired")
        
        if verification.attempts >= 5:
            raise ValueError("Maximum verification attempts exceeded")
        
        # Increment attempts
        verification.attempts += 1
        
        # Verify code
        if verification.code != code:
            self.db.commit()
            raise ValueError("Invalid verification code")
        
        # Mark as verified
        verification.verified = True
        verification.verified_at = datetime.utcnow()
        
        # Update user phone verification status (if we add this field)
        # For now, we just mark the SMS as verified
        
        self.db.commit()
        return True
    
    # Two Factor Authentication (HU002)
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
        
        # Verify password
        if not verify_password(password, user.password):
            raise ValueError("Invalid password")
        
        # Check if 2FA is already enabled
        existing_2fa = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        if existing_2fa and existing_2fa.enabled:
            raise ValueError("2FA is already enabled")
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Generate 10 backup codes (8 digits each)
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        backup_codes_json = json.dumps(backup_codes)
        
        # Create or update 2FA record
        if existing_2fa:
            existing_2fa.secret_key = secret
            existing_2fa.backup_codes = backup_codes_json
            existing_2fa.enabled = False
            existing_2fa.verified_at = None
            two_factor = existing_2fa
        else:
            two_factor = TwoFactorAuth(
                user_id=user_id,
                secret_key=secret,
                backup_codes=backup_codes_json,
                enabled=False
            )
            self.db.add(two_factor)
        
        self.db.flush()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        issuer_name = settings.PROJECT_NAME or "DflayerApi"
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=issuer_name
        )
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Convert to base64 data URI
        img_base64 = base64.b64encode(buffer.read()).decode()
        qr_code_url = f"data:image/png;base64,{img_base64}"
        
        return {
            "secret_key": secret,
            "qr_code_url": qr_code_url,
            "backup_codes": backup_codes,
            "message": "Scan the QR code with your authenticator app and verify with a code"
        }
    
    def verify_2fa_setup(self, user_id: int, code: str) -> bool:
        """
        Verifica y habilita el 2FA usando un código de la app autenticadora (HU002)
        
        El usuario debe escanear el QR y proporcionar un código de 6 dígitos
        para confirmar que configuró correctamente su app autenticadora.
        
        Args:
            user_id: ID del usuario
            code: Código de 6 dígitos de la app autenticadora
        
        Returns:
            True si la verificación fue exitosa
        
        Raises:
            ValueError: Si el usuario no tiene 2FA configurado, el código es inválido,
                       o el 2FA ya está habilitado
        """
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        if not two_factor:
            raise ValueError("2FA not configured. Please set it up first.")
        
        if two_factor.enabled:
            raise ValueError("2FA is already enabled")
        
        # Verify code
        totp = pyotp.TOTP(two_factor.secret_key)
        if not totp.verify(code, valid_window=1):
            raise ValueError("Invalid 2FA code")
        
        # Enable 2FA
        two_factor.enabled = True
        two_factor.verified_at = datetime.utcnow()
        
        # Update user's two_factor_enabled field
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.two_factor_enabled = True
            user.two_factor_secret = two_factor.secret_key
        
        self.db.commit()
        return True
    
    def verify_2fa_code(self, user_id: int, code: str) -> bool:
        """
        Verifica un código 2FA durante el login (HU002)
        
        Puede verificar tanto códigos TOTP de la app como códigos de respaldo.
        
        Args:
            user_id: ID del usuario
            code: Código de 6 dígitos (TOTP) o código de respaldo
        
        Returns:
            True si el código es válido, False en caso contrario
        """
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.enabled == True
        ).first()
        
        if not two_factor:
            return False
        
        # Try TOTP code first
        totp = pyotp.TOTP(two_factor.secret_key)
        if totp.verify(code, valid_window=1):
            return True
        
        # Try backup codes
        if two_factor.backup_codes:
            backup_codes = json.loads(two_factor.backup_codes)
            if code.upper() in backup_codes:
                # Remove used backup code
                backup_codes.remove(code.upper())
                two_factor.backup_codes = json.dumps(backup_codes) if backup_codes else None
                self.db.commit()
                return True
        
        return False
    
    def disable_2fa(self, user_id: int, password: str, code: str) -> bool:
        """
        Deshabilita el 2FA para un usuario (HU002)
        
        Requiere contraseña y código 2FA para confirmar la identidad.
        
        Args:
            user_id: ID del usuario
            password: Contraseña del usuario
            code: Código 2FA o código de respaldo
        
        Returns:
            True si el 2FA fue deshabilitado exitosamente
        
        Raises:
            ValueError: Si las credenciales son inválidas o el 2FA no está habilitado
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not verify_password(password, user.password):
            raise ValueError("Invalid password")
        
        two_factor = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.enabled == True
        ).first()
        
        if not two_factor:
            raise ValueError("2FA is not enabled")
        
        # Verify 2FA code
        if not self.verify_2fa_code(user_id, code):
            raise ValueError("Invalid 2FA code")
        
        # Disable 2FA
        two_factor.enabled = False
        user.two_factor_enabled = False
        user.two_factor_secret = None
        
        self.db.commit()
        return True
    
    # Password Reset (HU002)
    def request_password_reset(self, email: str) -> str:
        """
        Solicita un restablecimiento de contraseña (HU002)
        
        Genera un token de recuperación y envía un email al usuario
        con instrucciones para restablecer su contraseña.
        
        Args:
            email: Email del usuario que solicita el restablecimiento
        
        Returns:
            Token de recuperación generado
        
        Raises:
            ValueError: Si el usuario no existe
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Por seguridad, no revelamos si el email existe o no
            return secrets.token_urlsafe(32)  # Return dummy token
        
        # Invalidate old reset tokens
        old_resets = self.db.query(PasswordReset).filter(
            PasswordReset.user_id == user.user_id,
            PasswordReset.used == False
        ).all()
        for old_reset in old_resets:
            self.db.delete(old_reset)
        
        # Generate new reset token (valid for 1 hour)
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        password_reset = PasswordReset(
            user_id=user.user_id,
            token=reset_token,
            expires_at=expires_at,
            used=False
        )
        self.db.add(password_reset)
        self.db.commit()
        
        # Send password reset email
        email_service = UnifiedEmailService()
        email_service.send_password_reset_email(user.email, user.name, reset_token)
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Restablece la contraseña del usuario con un token (HU002)
        
        Valida el token de recuperación y actualiza la contraseña del usuario.
        
        Args:
            token: Token de recuperación recibido por email
            new_password: Nueva contraseña del usuario
        
        Returns:
            True si el restablecimiento fue exitoso
        
        Raises:
            ValueError: Si el token es inválido, expirado o ya fue usado
        """
        reset = self.db.query(PasswordReset).filter(
            PasswordReset.token == token
        ).first()
        
        if not reset:
            raise ValueError("Invalid reset token")
        
        if reset.is_expired():
            raise ValueError("Reset token has expired")
        
        if reset.used:
            raise ValueError("Reset token has already been used")
        
        # Update user password
        user = self.db.query(User).filter(User.user_id == reset.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.password = get_password_hash(new_password)
        
        # Mark token as used
        reset.used = True
        reset.used_at = datetime.utcnow()
        
        self.db.commit()
        return True

