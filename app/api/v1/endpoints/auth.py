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
    SMSVerificationRequest, SMSVerificationResponse,
    SendSMSVerificationRequest,
    TwoFactorSetupRequest, TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorDisableRequest,
    PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetResponse,
    UserInfo
)
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.user import User
# TwoFactorAuth removed - not in spec

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
    - Todos los usuarios se registran como tipo `usuario` por defecto
    - El tipo de usuario (`user_type`) es interno y solo puede ser modificado por administradores
    - TODOS los usuarios (admin y usuario) tienen EXACTAMENTE las mismas funcionalidades:
      * Crear contenido
      * Crear campañas publicitarias
      * Vender bonos
      * Ganar por interacciones
      * Invitar referidos
    - `is_business_account` es solo visual, no otorga permisos adicionales
    
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
    - **identify**: Correo electrónico o número de teléfono del usuario
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


# Email Verification Endpoints (HU001)
@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="Verificar correo electrónico",
    description="""
    **Verificación de Email (HU001)**
    
    Verifica el correo electrónico del usuario usando el token recibido por email.
    El token es válido por 10 minutos después de ser enviado.
    
    **Parámetros requeridos:**
    - **token**: Token de verificación recibido por email
    
    **Errores:**
    - 400: Si el token es inválido, expirado o ya fue usado
    """,
    response_description="Resultado de la verificación de email"
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        auth_service.verify_email(verification_data.token)
        return EmailVerificationResponse(
            verified=True,
            message="Email verified successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/resend-verification",
    summary="Reenviar correo de verificación",
    description="""
    **Reenvío de Verificación de Email (HU001)**
    
    Reenvía un nuevo correo de verificación al usuario.
    Invalida cualquier token de verificación anterior.
    
    **Parámetros requeridos:**
    - **email**: Email del usuario
    
    **Errores:**
    - 400: Si el usuario no existe o el email ya está verificado
    """,
    response_description="Mensaje de confirmación"
)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        token = auth_service.resend_verification_email(request.email)
        return {"message": "Verification email sent successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# SMS Verification Endpoints (HU001)
@router.post(
    "/send-sms-verification",
    summary="Enviar código de verificación por SMS",
    description="""
    **Envío de Código de Verificación SMS (HU001)**
    
    Envía un código de verificación de 6 dígitos por SMS al número de teléfono
    del usuario autenticado. El código es válido por 10 minutos.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido
    
    **Parámetros requeridos:**
    - **phone_number**: Número de teléfono donde enviar el código
    
    **Nota:** Si ya existe un código pendiente, se invalida y se genera uno nuevo.
    """,
    response_description="Confirmación de envío de código SMS"
)
async def send_sms_verification(
    request: SendSMSVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        code = auth_service.send_sms_verification_code(current_user.user_id, request.phone_number)
        return {"message": "SMS verification code sent successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/verify-sms",
    response_model=SMSVerificationResponse,
    summary="Verificar código SMS",
    description="""
    **Verificación de Código SMS (HU001)**
    
    Verifica el código de 6 dígitos recibido por SMS.
    El código debe ser válido y no expirado (10 minutos).
    Máximo 5 intentos de verificación.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido
    
    **Parámetros requeridos:**
    - **phone_number**: Número de teléfono a verificar
    - **code**: Código de 6 dígitos recibido por SMS
    
    **Errores:**
    - 400: Si el código es inválido, expirado o se excedieron los intentos
    """,
    response_description="Resultado de la verificación SMS"
)
async def verify_sms(
    verification_data: SMSVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        auth_service.verify_sms_code(
            current_user.user_id,
            verification_data.phone_number,
            verification_data.code
        )
        return SMSVerificationResponse(
            verified=True,
            message="Phone number verified successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Two Factor Authentication Endpoints (HU002)
@router.post(
    "/setup-2fa",
    response_model=TwoFactorSetupResponse,
    summary="Configurar autenticación de dos factores",
    description="""
    **Configuración de 2FA (HU002)**
    
    Configura la autenticación de dos factores para el usuario autenticado.
    Genera un código QR que debe ser escaneado con una app autenticadora
    (Google Authenticator, Authy, etc.) y 10 códigos de respaldo.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido
    
    **Parámetros requeridos:**
    - **password**: Contraseña del usuario para confirmar identidad
    
    **Respuesta:**
    - **secret_key**: Clave secreta para configuración manual
    - **qr_code_url**: URL del código QR en formato data URI (base64)
    - **backup_codes**: Lista de 10 códigos de respaldo (guardar de forma segura)
    
    **Nota:** El 2FA NO se habilita automáticamente. Debe usar `/verify-2fa-setup`
    con un código de la app para habilitarlo.
    """,
    response_description="Información de configuración de 2FA"
)
async def setup_2fa(
    request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        result = auth_service.setup_2fa(current_user.user_id, request.password)
        return TwoFactorSetupResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/verify-2fa-setup",
    summary="Verificar y habilitar 2FA",
    description="""
    **Verificación de Configuración de 2FA (HU002)**
    
    Verifica que el usuario configuró correctamente su app autenticadora
    y habilita el 2FA para su cuenta.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido
    
    **Parámetros requeridos:**
    - **code**: Código de 6 dígitos de la app autenticadora
    
    **Errores:**
    - 400: Si el código es inválido o el 2FA ya está habilitado
    """,
    response_description="Confirmación de habilitación de 2FA"
)
async def verify_2fa_setup(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        auth_service.verify_2fa_setup(current_user.user_id, request.code)
        return {"message": "2FA enabled successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/disable-2fa",
    summary="Deshabilitar autenticación de dos factores",
    description="""
    **Deshabilitación de 2FA (HU002)**
    
    Deshabilita la autenticación de dos factores para el usuario autenticado.
    Requiere contraseña y código 2FA para confirmar la identidad.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido
    
    **Parámetros requeridos:**
    - **password**: Contraseña del usuario
    - **code**: Código 2FA o código de respaldo
    
    **Errores:**
    - 400: Si las credenciales son inválidas o el 2FA no está habilitado
    """,
    response_description="Confirmación de deshabilitación de 2FA"
)
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        auth_service.disable_2fa(current_user.user_id, request.password, request.code)
        return {"message": "2FA disabled successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Password Reset Endpoints (HU002)
@router.post(
    "/request-password-reset",
    response_model=PasswordResetResponse,
    summary="Solicitar restablecimiento de contraseña",
    description="""
    **Solicitud de Restablecimiento de Contraseña (HU002)**
    
    Envía un email al usuario con un token para restablecer su contraseña.
    El token es válido por 1 hora.
    
    **Parámetros requeridos:**
    - **email**: Email del usuario
    
    **Nota de seguridad:**
    - Por seguridad, siempre retorna éxito incluso si el email no existe
    - Esto previene enumeración de usuarios
    """,
    response_description="Confirmación de solicitud de restablecimiento"
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    # Always return success for security (prevent user enumeration)
    auth_service.request_password_reset(request.email)
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent",
        success=True
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    summary="Restablecer contraseña",
    description="""
    **Restablecimiento de Contraseña (HU002)**
    
    Restablece la contraseña del usuario usando el token recibido por email.
    El token debe ser válido y no expirado (1 hora).
    
    **Parámetros requeridos:**
    - **token**: Token de recuperación recibido por email
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, mayúsculas, minúsculas, números)
    
    **Errores:**
    - 400: Si el token es inválido, expirado o ya fue usado
    - 400: Si la nueva contraseña no cumple los requisitos
    """,
    response_description="Resultado del restablecimiento de contraseña"
)
async def reset_password(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        auth_service.reset_password(request.token, request.new_password)
        return PasswordResetResponse(
            message="Password reset successfully",
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    - Tipo de usuario (usuario, admin)
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
    # TwoFactorAuth model removed - use user.two_factor_enabled field directly
    return UserInfo(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        username=current_user.username,
        user_type=current_user.user_type.value,
        level=current_user.level,
        email_verified=current_user.email_verified,
        two_factor_enabled=current_user.two_factor_enabled,  # Use field directly, model removed
        is_active=current_user.is_active,
        registration_date=current_user.registration_date
    )

