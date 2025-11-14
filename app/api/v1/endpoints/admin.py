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
from app.services.category_service import CategoryService
from app.services.user_upgrade_service import UserUpgradeService
from app.services.admin_user_service import AdminUserService
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListResponse
)
from app.schemas.user_upgrade import UserUpgradeResponse
from app.schemas.admin_user import (
    ChangeUserTypeRequest,
    ChangeUserTypeResponse,
    UserUpgradeListResponse,
    RejectUpgradeRequest
)

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


# Category Management Endpoints
@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría (Administrador)",
    description="""
    **Creación de Categoría (Solo Administradores)**
    
    Permite a los administradores crear nuevas categorías en el sistema.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros requeridos:**
    - **name**: Nombre de la categoría (debe ser único, 2-100 caracteres)
    
    **Parámetros opcionales:**
    - **description**: Descripción de la categoría (máximo 255 caracteres)
    - **icon**: Identificador o URL del icono (máximo 100 caracteres)
    
    **Uso:**
    - Las categorías se usan para clasificar contenido y definir intereses de usuarios
    - Los usuarios pueden seleccionar categorías como intereses en su perfil
    """,
    response_description="Categoría creada exitosamente"
)
async def create_category(
    category_data: CategoryCreateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    
    try:
        category = category_service.create_category(category_data)
        
        return CategoryResponse(
            category_id=category.category_id,
            name=category.name,
            description=category.description,
            icon=category.icon
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="Listar todas las categorías",
    description="""
    **Listado de Categorías**
    
    Obtiene una lista de todas las categorías disponibles en el sistema.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de consulta:**
    - **skip**: Número de registros a omitir (para paginación). Valor por defecto: 0
    - **limit**: Número máximo de registros a retornar. Valor por defecto: 100
    
    **Nota:** Este endpoint es accesible para todos los usuarios autenticados,
    pero solo los administradores pueden crear, actualizar o eliminar categorías.
    """,
    response_description="Lista de todas las categorías disponibles"
)
async def list_categories(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar (1-500)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    
    from app.models.category import Category
    # Get total count before pagination
    total = db.query(Category).count()
    
    categories = category_service.get_all_categories(skip, limit)
    
    return CategoryListResponse(
        categories=[
            CategoryResponse(
                category_id=cat.category_id,
                name=cat.name,
                description=cat.description,
                icon=cat.icon
            )
            for cat in categories
        ],
        total=total
    )


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Obtener categoría por ID",
    description="""
    **Consulta de Categoría por ID**
    
    Obtiene la información de una categoría específica por su ID.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **category_id**: ID único de la categoría a consultar
    
    **Errores:**
    - 404: Si la categoría no existe
    """,
    response_description="Información de la categoría solicitada"
)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    
    category = category_service.get_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategoryResponse(
        category_id=category.category_id,
        name=category.name,
        description=category.description,
        icon=category.icon
    )


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Actualizar categoría (Administrador)",
    description="""
    **Actualización de Categoría (Solo Administradores)**
    
    Permite a los administradores actualizar la información de una categoría existente.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **category_id**: ID único de la categoría a actualizar
    
    **Parámetros opcionales (solo se actualizan los campos proporcionados):**
    - **name**: Nuevo nombre de la categoría
    - **description**: Nueva descripción
    - **icon**: Nuevo icono
    
    **Errores:**
    - 404: Si la categoría no existe
    - 400: Si el nuevo nombre ya está en uso por otra categoría
    """,
    response_description="Categoría actualizada exitosamente"
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    
    try:
        category = category_service.update_category(category_id, category_data)
        
        return CategoryResponse(
            category_id=category.category_id,
            name=category.name,
            description=category.description,
            icon=category.icon
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría (Administrador)",
    description="""
    **Eliminación de Categoría (Solo Administradores)**
    
    Permite a los administradores eliminar una categoría del sistema.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **category_id**: ID único de la categoría a eliminar
    
    **Restricciones:**
    - No se puede eliminar una categoría que esté asociada con usuarios (intereses)
    - Si la categoría está en uso, se retornará un error 400
    
    **Errores:**
    - 404: Si la categoría no existe
    - 400: Si la categoría está en uso por usuarios
    """,
    response_description="Categoría eliminada exitosamente (sin cuerpo de respuesta)"
)
async def delete_category(
    category_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category_service = CategoryService(db)
    
    try:
        category_service.delete_category(category_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# User Management Endpoints
@router.post(
    "/users/change-type",
    response_model=ChangeUserTypeResponse,
    summary="Cambiar tipo de usuario (Administrador)",
    description="""
    **Cambio de Tipo de Usuario (Solo Administradores)**
    
    Permite a los administradores cambiar el tipo de usuario de cualquier usuario en el sistema.
    Puede cambiar cualquier usuario (client, merchant, affiliate) a cualquier tipo,
    incluyendo crear nuevos administradores.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros requeridos:**
    - **user_id**: ID del usuario cuyo tipo se va a cambiar
    - **new_user_type**: Nuevo tipo de usuario. Valores permitidos:
      - `client`: Usuario normal
      - `merchant`: Comercio/empresa
      - `affiliate`: Creador de contenido/afiliado
      - `admin`: Administrador del sistema
    
    **Parámetros opcionales:**
    - **reason**: Razón del cambio (para auditoría)
    
    **Restricciones:**
    - Un administrador no puede cambiar su propio tipo de usuario
    - Se recomienda tener cuidado al crear nuevos administradores
    
    **Nota:** Si el usuario tiene una solicitud de upgrade pendiente y el cambio coincide
    con la solicitud, esta se aprobará automáticamente.
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


@router.get(
    "/users/upgrade-requests",
    response_model=UserUpgradeListResponse,
    summary="Listar solicitudes de upgrade (Administrador)",
    description="""
    **Listado de Solicitudes de Upgrade (Solo Administradores)**
    
    Obtiene todas las solicitudes de cambio de tipo de usuario (client -> merchant/affiliate).
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de consulta:**
    - **status**: (Opcional) Filtrar por estado. Valores: `pending`, `approved`, `rejected`
    - **skip**: Número de registros a omitir (paginación). Valor por defecto: 0
    - **limit**: Número máximo de registros a retornar. Valor por defecto: 100
    
    **Respuesta:**
    - Lista de solicitudes de upgrade con información del usuario y estado
    - Contadores de solicitudes por estado (pending, approved, rejected)
    """,
    response_description="Lista de solicitudes de upgrade"
)
async def list_upgrade_requests(
    status: str = Query(None, description="Filtrar por estado (pending, approved, rejected)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    admin_service = AdminUserService(db)
    
    upgrade_requests = admin_service.get_all_upgrade_requests(status, skip, limit)
    
    # Get counts
    from app.models.user_upgrade import UserUpgradeRequest, UpgradeRequestStatus
    total = db.query(UserUpgradeRequest).count()
    pending_count = db.query(UserUpgradeRequest).filter(
        UserUpgradeRequest.status == UpgradeRequestStatus.PENDING
    ).count()
    approved_count = db.query(UserUpgradeRequest).filter(
        UserUpgradeRequest.status == UpgradeRequestStatus.APPROVED
    ).count()
    rejected_count = db.query(UserUpgradeRequest).filter(
        UserUpgradeRequest.status == UpgradeRequestStatus.REJECTED
    ).count()
    
    return UserUpgradeListResponse(
        upgrade_requests=[
            {
                "upgrade_request_id": req.upgrade_request_id,
                "user_id": req.user_id,
                "user_name": req.user.name if req.user else None,
                "user_email": req.user.email if req.user else None,
                "current_user_type": req.current_user_type,
                "requested_user_type": req.requested_user_type,
                "status": req.status.value,
                "reason": req.reason,
                "business_name": req.business_name,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
                "rejection_reason": req.rejection_reason
            }
            for req in upgrade_requests
        ],
        total=total,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


@router.post(
    "/users/upgrade-requests/{upgrade_request_id}/approve",
    response_model=UserUpgradeResponse,
    summary="Aprobar solicitud de upgrade (Administrador)",
    description="""
    **Aprobación de Solicitud de Upgrade (Solo Administradores)**
    
    Aprueba una solicitud de cambio de tipo de usuario (client -> merchant/affiliate).
    Al aprobar, el tipo de usuario del solicitante cambia automáticamente.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **upgrade_request_id**: ID de la solicitud de upgrade a aprobar
    
    **Errores:**
    - 404: Si la solicitud no existe
    - 400: Si la solicitud ya fue procesada (aprobada o rechazada)
    """,
    response_description="Solicitud aprobada y tipo de usuario actualizado"
)
async def approve_upgrade_request(
    upgrade_request_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    upgrade_service = UserUpgradeService(db)
    
    try:
        updated_user = upgrade_service.approve_upgrade(
            upgrade_request_id=upgrade_request_id,
            admin_user_id=admin_user.user_id
        )
        
        return UserUpgradeResponse(
            upgrade_request_id=upgrade_request_id,
            user_id=updated_user.user_id,
            current_user_type=updated_user.user_type.value,
            requested_user_type=updated_user.user_type.value,
            status="approved",
            message=f"User type successfully changed to '{updated_user.user_type.value}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/users/upgrade-requests/{upgrade_request_id}/reject",
    response_model=UserUpgradeResponse,
    summary="Rechazar solicitud de upgrade (Administrador)",
    description="""
    **Rechazo de Solicitud de Upgrade (Solo Administradores)**
    
    Rechaza una solicitud de cambio de tipo de usuario.
    El tipo de usuario del solicitante NO cambia.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    - El usuario debe ser de tipo `admin`
    
    **Parámetros de ruta:**
    - **upgrade_request_id**: ID de la solicitud de upgrade a rechazar
    
    **Parámetros del cuerpo (JSON, opcional):**
    - **rejection_reason**: Razón del rechazo
    
    **Errores:**
    - 404: Si la solicitud no existe
    - 400: Si la solicitud ya fue procesada (aprobada o rechazada)
    """,
    response_description="Solicitud rechazada"
)
async def reject_upgrade_request(
    upgrade_request_id: int,
    reject_data: RejectUpgradeRequest = None,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    upgrade_service = UserUpgradeService(db)
    
    rejection_reason = reject_data.rejection_reason if reject_data else None
    
    try:
        upgrade_request = upgrade_service.reject_upgrade(
            upgrade_request_id=upgrade_request_id,
            admin_user_id=admin_user.user_id,
            rejection_reason=rejection_reason or "Rejected by administrator"
        )
        
        return UserUpgradeResponse(
            upgrade_request_id=upgrade_request.upgrade_request_id,
            user_id=upgrade_request.user_id,
            current_user_type=upgrade_request.current_user_type,
            requested_user_type=upgrade_request.requested_user_type,
            status="rejected",
            message=f"Upgrade request rejected. Reason: {upgrade_request.rejection_reason}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

