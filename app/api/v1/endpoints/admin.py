"""
Administrative Endpoints
Handles administrative operations (categories, users, etc.)
Only accessible by administrators
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserType
# CategoryService removed - Category model not in spec
from app.services.admin_user_service import AdminUserService
from app.services.tax_data_service import TaxDataService
# Category schemas removed - Category model not in spec
from app.schemas.admin_user import (
    ChangeUserTypeRequest,
    ChangeUserTypeResponse,
    PromoteRequest
)
from app.schemas.tax_data import TaxDataResponse
from app.models.tax_data import TaxDataVerificationStatus

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency para verificar que el usuario es administrador
    
    Args:
        current_user: Usuario autenticado
    
    Returns:
        Usuario si es administrador
    
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires administrator privileges"
        )
    return current_user


# Category Management Endpoints - REMOVED (Category model not in spec)
# All category endpoints removed as Category model doesn't exist in ANÁLISIS COMPLETO DEL.txt


# User Management Endpoints
@router.post(
    "/users/change-type",
    response_model=ChangeUserTypeResponse,
    summary="Cambiar tipo de usuario (Administrador)",
    description="""
    **Cambio de Tipo de Usuario (Solo Administradores)**
    
    Permite a los administradores cambiar el tipo de usuario de cualquier usuario en el sistema.
    Puede cambiar cualquier usuario a 'usuario' o 'admin'.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros requeridos:**
    - **user_id**: ID del usuario cuyo tipo se va a cambiar
    - **new_user_type**: Nuevo tipo de usuario. Valores permitidos:
      - `usuario`: Usuario estándar (puede crear contenido, campañas, bonos, monetizar)
      - `admin`: Administrador (puede administrar contenido y cambiar tipos de usuario)
    
    **NOTA IMPORTANTE:**
    - TODOS los usuarios (admin y usuario) tienen EXACTAMENTE las mismas funcionalidades
    - La diferencia es que admin puede administrar contenido y cambiar tipos de usuario
    - is_business_account es solo visual, no afecta permisos
    
    **Parámetros opcionales:**
    - **reason**: Razón del cambio (para auditoría)
    
    **Restricciones:**
    - Un administrador no puede cambiar su propio tipo de usuario
    - Se recomienda tener cuidado al crear nuevos administradores
    """,
    response_description="Tipo de usuario cambiado exitosamente"
)
async def change_user_type(
    change_request: ChangeUserTypeRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminUserService(db)
    
    try:
        updated_user = admin_service.change_user_type(
            target_user_id=change_request.user_id,
            new_user_type=change_request.new_user_type,
            admin_user_id=admin_user.user_id,
            reason=change_request.reason
        )
        
        return ChangeUserTypeResponse(
            user_id=updated_user.user_id,
            previous_user_type="unknown",  # Would need audit log to track this properly
            new_user_type=updated_user.user_type.value,
            changed_by=admin_user.user_id,
            message=f"User type changed successfully to '{updated_user.user_type.value}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/users/{user_id}/create-admin",
    response_model=ChangeUserTypeResponse,
    summary="Crear administrador (Administrador)",
    description="""
    **Creación de Administrador (Solo Administradores)**
    
    Permite a los administradores convertir cualquier usuario en administrador.
    Este es un endpoint específico y simplificado para el caso común de crear administradores.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **user_id**: ID del usuario a convertir en administrador
    
    **Parámetros del cuerpo (JSON, opcional):**
    - **reason**: Razón de la promoción (para auditoría)
    
    **NOTA IMPORTANTE:**
    - Solo existen 2 tipos: 'admin' y 'usuario'
    - TODOS los usuarios tienen las mismas funcionalidades (crear contenido, campañas, bonos)
    - La diferencia es que admin puede administrar contenido y cambiar tipos de usuario
    
    **Uso alternativo:** Para cambiar cualquier tipo a cualquier tipo, use el endpoint
    `/api/v1/admin/users/change-type` que es más flexible.
    """,
    response_description="Usuario convertido a administrador exitosamente"
)
async def create_admin(
    user_id: int,
    promote_data: PromoteRequest = None,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminUserService(db)
    
    # Verify user exists
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        updated_user = admin_service.create_admin(
            user_id=user_id,
            admin_id=admin_user.user_id,
            reason=promote_data.reason if promote_data else None
        )
        
        return ChangeUserTypeResponse(
            user_id=updated_user.user_id,
            previous_user_type=target_user.user_type.value,
            new_user_type=updated_user.user_type.value,
            changed_by=admin_user.user_id,
            message=f"User successfully converted to 'admin'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Tax Data Verification Endpoints (HU005)

@router.post(
    "/tax-data/{user_id}/verify",
    response_model=TaxDataResponse,
    summary="Validar datos fiscales (Administrador)",
    description="""
    **Validar Datos Fiscales (HU005 - Solo Administradores)**
    
    Permite a los administradores validar los datos fiscales de un usuario.
    Una vez validados, el usuario puede recibir pagos.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **user_id**: ID del usuario cuyos datos fiscales se van a validar
    
    **Comportamiento:**
    - Cambia el estado de validación a **VERIFIED**
    - Registra la fecha de verificación
    - Limpia cualquier motivo de rechazo previo
    
    **Errores:**
    - Si el usuario no existe, retorna 404
    - Si el usuario no tiene datos fiscales, retorna 400
    """,
    response_description="Datos fiscales validados exitosamente"
)
async def verify_tax_data(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    try:
        tax_data = tax_service.update_verification_status(
            user_id=user_id,
            status=TaxDataVerificationStatus.VERIFIED
        )
        
        return TaxDataResponse(
            tax_data_id=tax_data.tax_data_id,
            document_type=tax_data.document_type.value if tax_data.document_type else None,
            tax_identification_number=tax_data.tax_identification_number,
            tax_regime=tax_data.tax_regime.value if tax_data.tax_regime else None,
            rut_document_url=tax_data.rut_document_url,
            bank_name=tax_data.bank_name,
            bank_account_type=tax_data.bank_account_type.value if tax_data.bank_account_type else None,
            bank_account_number=tax_data.bank_account_number,
            bank_account_holder=tax_data.bank_account_holder,
            verification_status=tax_data.verification_status.value if tax_data.verification_status else "pending",
            verified_at=tax_data.verified_at,
            rejection_reason=tax_data.rejection_reason,
            withholding_percentage=tax_data.withholding_percentage,
            is_iva_responsible=tax_data.is_iva_responsible,
            created_at=tax_data.created_at,
            updated_at=tax_data.updated_at,
            # Legacy fields
            document=tax_data.document,
            bank_account=tax_data.bank_account,
            withholdings=tax_data.withholding_percentage,
            verified=(tax_data.verification_status.value == "verified" if tax_data.verification_status else False)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/tax-data/{user_id}/reject",
    response_model=TaxDataResponse,
    summary="Rechazar datos fiscales (Administrador)",
    description="""
    **Rechazar Datos Fiscales (HU005 - Solo Administradores)**
    
    Permite a los administradores rechazar los datos fiscales de un usuario.
    Debe proporcionar un motivo de rechazo.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **user_id**: ID del usuario cuyos datos fiscales se van a rechazar
    
    **Parámetros de query:**
    - **rejection_reason**: Motivo del rechazo (mínimo 10, máximo 500 caracteres)
    
    **Comportamiento:**
    - Cambia el estado de validación a **REJECTED**
    - Registra la fecha de rechazo
    - Guarda el motivo de rechazo para que el usuario pueda corregir
    
    **Errores:**
    - Si el usuario no existe, retorna 404
    - Si el usuario no tiene datos fiscales, retorna 400
    - Si no se proporciona motivo de rechazo, retorna 400
    """,
    response_description="Datos fiscales rechazados"
)
async def reject_tax_data(
    user_id: int,
    rejection_reason: str = Query(..., min_length=10, max_length=500, description="Motivo del rechazo"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    try:
        tax_data = tax_service.update_verification_status(
            user_id=user_id,
            status=TaxDataVerificationStatus.REJECTED,
            rejection_reason=rejection_reason
        )
        
        return TaxDataResponse(
            tax_data_id=tax_data.tax_data_id,
            document_type=tax_data.document_type.value if tax_data.document_type else None,
            tax_identification_number=tax_data.tax_identification_number,
            tax_regime=tax_data.tax_regime.value if tax_data.tax_regime else None,
            rut_document_url=tax_data.rut_document_url,
            bank_name=tax_data.bank_name,
            bank_account_type=tax_data.bank_account_type.value if tax_data.bank_account_type else None,
            bank_account_number=tax_data.bank_account_number,
            bank_account_holder=tax_data.bank_account_holder,
            verification_status=tax_data.verification_status.value if tax_data.verification_status else "pending",
            verified_at=tax_data.verified_at,
            rejection_reason=tax_data.rejection_reason,
            withholding_percentage=tax_data.withholding_percentage,
            is_iva_responsible=tax_data.is_iva_responsible,
            created_at=tax_data.created_at,
            updated_at=tax_data.updated_at,
            # Legacy fields
            document=tax_data.document,
            bank_account=tax_data.bank_account,
            withholdings=tax_data.withholding_percentage,
            verified=(tax_data.verification_status.value == "verified" if tax_data.verification_status else False)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



