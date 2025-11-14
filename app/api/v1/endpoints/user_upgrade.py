"""
User Upgrade Endpoints
Handles user requests to upgrade from client to merchant or affiliate
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.user_upgrade_service import UserUpgradeService
from app.schemas.user_upgrade import (
    UserUpgradeRequest,
    UserUpgradeResponse,
    UserUpgradeStatusResponse
)

router = APIRouter()


@router.post(
    "/request",
    response_model=UserUpgradeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar cambio de tipo de usuario",
    description="""
    **Solicitud de Cambio de Tipo de Usuario**
    
    Permite a usuarios tipo 'client' solicitar cambiar su tipo de usuario a 'merchant' o 'affiliate'.
    La solicitud queda en estado 'pending' hasta que un administrador la apruebe o rechace.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Restricciones:**
    - Solo usuarios tipo 'client' pueden solicitar upgrade
    - No se puede tener más de una solicitud pendiente a la vez
    - Si ya tienes una solicitud aprobada, no puedes solicitar otro cambio
    
    **Parámetros requeridos:**
    - **target_user_type**: Tipo de usuario objetivo. Valores permitidos: `merchant` o `affiliate`
    
    **Parámetros opcionales:**
    - **reason**: Razón o justificación para el cambio
    - **business_name**: Nombre del negocio (recomendado para merchant)
    - **business_description**: Descripción del negocio o actividad
    
    **Proceso:**
    1. El usuario envía la solicitud
    2. Un administrador revisa y aprueba/rechaza la solicitud
    3. Si es aprobada, el tipo de usuario cambia automáticamente
    4. El usuario recibe notificación del resultado
    
    **Nota:** Los administradores pueden cambiar tipos de usuario directamente
    sin necesidad de solicitud en `/api/v1/admin/users/change-type`
    """,
    response_description="Solicitud de upgrade creada exitosamente"
)
async def request_upgrade(
    upgrade_data: UserUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upgrade_service = UserUpgradeService(db)
    
    try:
        upgrade_request = upgrade_service.request_upgrade(
            user_id=current_user.user_id,
            upgrade_data=upgrade_data
        )
        
        return UserUpgradeResponse(
            upgrade_request_id=upgrade_request.upgrade_request_id,
            user_id=upgrade_request.user_id,
            current_user_type=upgrade_request.current_user_type,
            requested_user_type=upgrade_request.requested_user_type,
            status=upgrade_request.status.value,
            message=f"Upgrade request to '{upgrade_request.requested_user_type}' submitted successfully. Waiting for admin approval."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/status",
    response_model=UserUpgradeStatusResponse,
    summary="Consultar estado de solicitud de upgrade",
    description="""
    **Consulta de Estado de Solicitud de Upgrade**
    
    Permite a un usuario consultar el estado de su solicitud de cambio de tipo de usuario.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Respuesta:**
    - **has_pending_request**: True si hay una solicitud pendiente
    - **current_user_type**: Tipo de usuario actual
    - **requested_user_type**: Tipo de usuario solicitado (si hay solicitud)
    - **status**: Estado de la solicitud (pending, approved, rejected)
    - **message**: Mensaje informativo sobre el estado
    """,
    response_description="Estado de la solicitud de upgrade del usuario"
)
async def get_upgrade_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upgrade_service = UserUpgradeService(db)
    
    upgrade_request = upgrade_service.get_user_upgrade_status(current_user.user_id)
    
    if not upgrade_request:
        return UserUpgradeStatusResponse(
            has_pending_request=False,
            current_user_type=current_user.user_type.value,
            requested_user_type=None,
            status=None,
            message="No upgrade request found"
        )
    
    # Determine message based on status
    if upgrade_request.status.value == "pending":
        message = f"Your request to become '{upgrade_request.requested_user_type}' is pending admin review"
    elif upgrade_request.status.value == "approved":
        message = f"Your request to become '{upgrade_request.requested_user_type}' has been approved!"
    else:
        message = f"Your request to become '{upgrade_request.requested_user_type}' was rejected"
        if upgrade_request.rejection_reason:
            message += f". Reason: {upgrade_request.rejection_reason}"
    
    return UserUpgradeStatusResponse(
        has_pending_request=upgrade_request.status.value == "pending",
        current_user_type=current_user.user_type.value,
        requested_user_type=upgrade_request.requested_user_type,
        status=upgrade_request.status.value,
        message=message
    )

