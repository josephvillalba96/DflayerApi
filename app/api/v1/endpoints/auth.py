"""
Authentication Endpoints
Handles registration, login, email verification, 2FA, and password reset
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
from app.core.config import settings
from app.models.user import User
from app.models.two_factor_auth import TwoFactorAuth

router = APIRouter()
security = HTTPBearer()


def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extrae el token del header de autorización
    
    HTTPBearer automáticamente maneja el formato "Bearer <token>",
    pero esta función extrae solo el token.
    
    Args:
        credentials: Credenciales HTTPBearer de FastAPI
    
    Returns:
        Token JWT como string (sin el prefijo "Bearer")
    
    Raises:
        HTTPException: Si las credenciales no son válidas
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionaron credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# Dependency to get current user
async def get_current_user(
    token: str = Depends(get_token),
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
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="""
    **Registro de Usuario (HU001)**
    
    Permite registrar un nuevo usuario en el sistema. Al completar el registro:
    
    - Se crea el usuario con nivel 1 automáticamente
    - Se genera una sesión inmediata (se retorna un token de acceso)
    - Se envía un correo electrónico de verificación automáticamente
    
    **Parámetros requeridos:**
    - **email**: Correo electrónico del usuario (debe ser único en el sistema)
    - **password**: Contraseña (mínimo 8 caracteres, debe contener mayúsculas, minúsculas y un dígito)
    - **name**: Nombre completo del usuario
    - **username**: Nombre de usuario (mínimo 3 caracteres, solo alfanuméricos y guión bajo)
    
    **Nota importante:**
    - Todos los usuarios se registran como tipo `client` por defecto
    - El tipo de usuario (`user_type`) es interno y solo puede ser modificado por administradores
    - Para cambiar a `merchant` o `affiliate`, contacte con un administrador
    
    **Respuesta:**
    - Retorna un token de acceso JWT que permite autenticarse inmediatamente
    - El usuario queda en sesión activa después del registro
    - El correo de verificación se envía automáticamente al email proporcionado
    """,
    response_description="Token de acceso y información del usuario registrado"
)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        user, verification_token, access_token = auth_service.register_user(user_data)
        
        # Email sent automatically via AuthService
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.user_id,
            email=user.email,
            user_type=user.user_type.value,
            email_verified=user.email_verified,
            two_factor_required=False
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Login Endpoints
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="""
    **Inicio de Sesión (HU002)**
    
    Permite a un usuario autenticarse en el sistema usando su correo electrónico y contraseña.
    
    **Parámetros requeridos:**
    - **email**: Correo electrónico del usuario
    - **password**: Contraseña del usuario
    
    **Parámetros opcionales:**
    - **two_factor_code**: Código de autenticación de dos factores (requerido si el usuario tiene 2FA habilitado)
    
    **Comportamiento:**
    - Si las credenciales son correctas y el usuario NO tiene 2FA habilitado, retorna el token de acceso inmediatamente
    - Si el usuario tiene 2FA habilitado y no se proporciona el código, retorna un error 202 con el header `X-2FA-Required: true`
    - Si se proporciona el código 2FA y es válido, retorna el token de acceso
    
    **Respuesta:**
    - Token de acceso JWT con información del usuario
    - Información sobre el estado de verificación de email y 2FA
    """,
    response_description="Token de acceso y información del usuario autenticado"
)
async def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
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
@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="Verificar correo electrónico",
    description="""
    **Verificación de Correo Electrónico (HU001)**
    
    Permite verificar el correo electrónico de un usuario usando el token de verificación enviado por email.
    
    **Parámetros requeridos:**
    - **token**: Token de verificación recibido en el correo electrónico de registro
    
    **Comportamiento:**
    - Valida el token de verificación
    - Si el token es válido y no ha expirado, marca el correo como verificado
    - Los tokens de verificación expiran después de 7 días
    
    **Respuesta:**
    - Confirma si la verificación fue exitosa
    - Proporciona un mensaje de confirmación
    """,
    response_description="Resultado de la verificación del correo electrónico"
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
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


@router.post(
    "/resend-verification",
    summary="Reenviar correo de verificación",
    description="""
    **Reenvío de Correo de Verificación (HU001)**
    
    Permite reenviar el correo electrónico de verificación a un usuario que no lo recibió o cuyo token expiró.
    
    **Parámetros requeridos:**
    - **email**: Correo electrónico del usuario que solicita el reenvío
    
    **Comportamiento:**
    - Genera un nuevo token de verificación
    - Envía un nuevo correo electrónico con el token
    - El nuevo token tiene validez de 7 días
    
    **Nota:** Este endpoint siempre retorna éxito para prevenir la enumeración de emails.
    """,
    response_description="Confirmación de que el correo de verificación fue enviado"
)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
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
@router.post(
    "/2fa/setup",
    response_model=TwoFactorSetupResponse,
    summary="Configurar autenticación de dos factores",
    description="""
    **Configuración de Autenticación de Dos Factores (HU002)**
    
    Permite configurar la autenticación de dos factores (2FA) para la cuenta del usuario autenticado.
    
    **Parámetros requeridos:**
    - **password**: Contraseña del usuario para confirmar la identidad
    
    **Comportamiento:**
    - Genera una clave secreta única para el usuario
    - Crea un código QR que debe ser escaneado con una aplicación autenticadora (Google Authenticator, Authy, etc.)
    - Genera códigos de respaldo que deben guardarse de forma segura
    - El 2FA NO se habilita automáticamente; el usuario debe verificar con un código primero
    
    **Pasos siguientes:**
    1. Escanear el código QR con una aplicación autenticadora
    2. Usar el endpoint `/2fa/verify` con un código generado por la app para habilitar el 2FA
    
    **Respuesta:**
    - URL del código QR para escanear
    - Clave secreta (para configuración manual si es necesario)
    - Lista de códigos de respaldo (guardar de forma segura)
    """,
    response_description="Información de configuración de 2FA incluyendo QR code y códigos de respaldo"
)
async def setup_2fa(
    request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


@router.post(
    "/2fa/verify",
    summary="Verificar y habilitar 2FA",
    description="""
    **Verificación y Habilitación de 2FA (HU002)**
    
    Verifica que el usuario haya configurado correctamente su aplicación autenticadora y habilita el 2FA.
    
    **Parámetros requeridos:**
    - **code**: Código de 6 dígitos generado por la aplicación autenticadora después de escanear el QR
    
    **Comportamiento:**
    - Valida el código proporcionado contra la clave secreta generada
    - Si el código es válido, habilita permanentemente el 2FA para la cuenta
    - A partir de este momento, el usuario necesitará proporcionar un código 2FA al iniciar sesión
    
    **Nota:** Una vez habilitado, el 2FA solo puede deshabilitarse usando el endpoint `/2fa/disable` con la contraseña y un código válido.
    """,
    response_description="Confirmación de que el 2FA fue habilitado exitosamente"
)
async def verify_2fa_setup(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


@router.post(
    "/2fa/disable",
    summary="Deshabilitar autenticación de dos factores",
    description="""
    **Deshabilitación de 2FA (HU002)**
    
    Permite deshabilitar la autenticación de dos factores para la cuenta del usuario.
    
    **Parámetros requeridos:**
    - **password**: Contraseña del usuario para confirmar la identidad
    - **code**: Código 2FA de 6 dígitos de la aplicación autenticadora O uno de los códigos de respaldo
    
    **Comportamiento:**
    - Valida tanto la contraseña como el código 2FA
    - Si ambos son correctos, deshabilita el 2FA permanentemente
    - El usuario podrá iniciar sesión solo con email y contraseña después de esto
    
    **Seguridad:**
    - Requiere ambos factores (contraseña + código) para prevenir deshabilitación no autorizada
    - Acepta códigos de respaldo en caso de pérdida del dispositivo autenticador
    """,
    response_description="Confirmación de que el 2FA fue deshabilitado exitosamente"
)
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


@router.get(
    "/2fa/status",
    summary="Obtener estado de 2FA",
    description="""
    **Estado de Autenticación de Dos Factores**
    
    Obtiene el estado actual de la configuración de 2FA para el usuario autenticado.
    
    **Respuesta:**
    - **enabled**: Indica si el 2FA está actualmente habilitado y activo
    - **setup**: Indica si el usuario ha iniciado el proceso de configuración de 2FA (aunque no esté habilitado)
    
    **Casos de uso:**
    - Verificar si el usuario necesita configurar 2FA
    - Verificar si el 2FA está activo antes de requerir código en el login
    """,
    response_description="Estado actual de la configuración de 2FA del usuario"
)
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    two_factor = db.query(TwoFactorAuth).filter(
        TwoFactorAuth.user_id == current_user.user_id
    ).first()
    
    return {
        "enabled": two_factor.enabled if two_factor else False,
        "setup": two_factor is not None
    }


# Password Reset Endpoints
@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponse,
    summary="Solicitar restablecimiento de contraseña",
    description="""
    **Solicitud de Restablecimiento de Contraseña (HU002)**
    
    Permite solicitar el restablecimiento de contraseña cuando el usuario la ha olvidado.
    
    **Parámetros requeridos:**
    - **email**: Correo electrónico de la cuenta para la cual se solicita el restablecimiento
    
    **Comportamiento:**
    - Si el email existe en el sistema, genera un token de restablecimiento
    - Envía un correo electrónico con un enlace para restablecer la contraseña
    - El token tiene validez de 24 horas
    
    **Seguridad:**
    - Este endpoint siempre retorna éxito para prevenir la enumeración de emails
    - El mensaje de respuesta es genérico independientemente de si el email existe o no
    
    **Pasos siguientes:**
    - El usuario debe hacer clic en el enlace del correo o usar el endpoint `/password-reset/confirm` con el token
    """,
    response_description="Confirmación de que la solicitud fue procesada (siempre retorna éxito por seguridad)"
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    token = auth_service.request_password_reset(request.email)
    
    # Email sent automatically via AuthService
    # Always return success to prevent email enumeration
    
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent",
        success=True
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetResponse,
    summary="Confirmar restablecimiento de contraseña",
    description="""
    **Confirmación de Restablecimiento de Contraseña (HU002)**
    
    Permite establecer una nueva contraseña usando el token recibido por correo electrónico.
    
    **Parámetros requeridos:**
    - **token**: Token de restablecimiento recibido en el correo electrónico
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, debe contener mayúsculas, minúsculas y un dígito)
    
    **Comportamiento:**
    - Valida el token de restablecimiento
    - Si el token es válido y no ha expirado, actualiza la contraseña del usuario
    - Los tokens expiran después de 24 horas
    - Después de restablecer la contraseña, el usuario debe iniciar sesión con la nueva contraseña
    
    **Seguridad:**
    - El token solo puede usarse una vez
    - Después de restablecer, todos los tokens de sesión anteriores se invalidan
    """,
    response_description="Confirmación de que la contraseña fue restablecida exitosamente"
)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
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
@router.get(
    "/me",
    response_model=UserInfo,
    summary="Obtener información del usuario actual",
    description="""
    **Información del Usuario Autenticado**
    
    Obtiene la información completa del usuario actualmente autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Información retornada:**
    - ID del usuario
    - Email y nombre de usuario
    - Nombre completo
    - Tipo de usuario (client, merchant, affiliate)
    - Nivel del usuario en el sistema
    - Estado de verificación de email
    - Estado de habilitación de 2FA
    - Estado de activación de la cuenta
    - Fecha de registro
    
    **Uso típico:**
    - Obtener información del perfil del usuario
    - Verificar estado de verificación y seguridad
    - Mostrar información en el dashboard del usuario
    """,
    response_description="Información completa del usuario autenticado"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

