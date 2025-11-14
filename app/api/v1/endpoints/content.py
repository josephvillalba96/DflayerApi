"""
Content Endpoints (HU006)
Handles content creation and management for authenticated merchants/affiliates
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.content_service import ContentService
from app.schemas.content import (
    ContentCreateRequest,
    ContentUpdateRequest,
    ContentResponse,
    ContentListResponse
)

router = APIRouter()


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear contenido",
    description="""
    **Creación de Contenido (HU006)**
    
    Permite a comerciantes y afiliados crear publicaciones de contenido en la plataforma.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Permisos:**
    - Todos los usuarios autenticados pueden crear contenido (client, merchant, affiliate, admin)
    - No hay restricciones de tipo de usuario para crear contenido
    
    **Parámetros requeridos:**
    - **content_type**: Tipo de contenido. Valores permitidos: `video`, `image`, `text`, `audio`
    
    **Parámetros opcionales:**
    - **title**: Título del contenido
    - **description**: Descripción o texto del contenido
    - **url**: URL del contenido si ya fue subido a un servicio de almacenamiento (S3, etc.)
    - **thumbnail_url**: URL de la imagen miniatura (para videos principalmente)
    - **visibility**: Visibilidad del contenido. Valores: `public` (por defecto), `private`
    - **allow_comments**: Permitir comentarios en el contenido (por defecto: true)
    - **location_id**: ID de ubicación para geotagging (opcional)
    - **category_ids**: Lista de IDs de categorías para clasificar el contenido
    - **hashtags**: Lista de hashtags (deben comenzar con #, ejemplo: ["#tecnologia", "#video"])
    - **scheduled_publish_at**: Fecha y hora programada para publicar el contenido (formato ISO 8601)
    - **target_audience**: Descripción de la audiencia objetivo del contenido
    
    **Comportamiento:**
    - Crea un nuevo registro de contenido asociado al usuario autenticado
    - Si se proporcionan hashtags, se crean o asocian automáticamente
    - Si se proporciona `scheduled_publish_at`, el contenido se publicará en esa fecha
    - El contenido queda activo inmediatamente a menos que esté programado
    
    **Nota:** El contenido multimedia debe subirse primero a un servicio de almacenamiento (S3) y luego proporcionar la URL.
    """,
    response_description="Contenido creado con toda su información y metadatos"
)
async def create_content(
    content_data: ContentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    
    try:
        content = content_service.create_content(current_user.user_id, content_data)
        
        # Get hashtags
        hashtags = []
        if content.hashtags:
            hashtags = [ch.hashtag.name for ch in content.hashtags]
        
        return ContentResponse(
            content_id=content.content_id,
            merchant_id=content.merchant_id,
            merchant_name=current_user.name,
            content_type=content.content_type.value,
            url=content.url,
            title=content.title,
            description=content.description,
            thumbnail_url=content.thumbnail_url,
            duration=content.duration,
            format=content.format,
            resolution=content.resolution,
            visibility=content.visibility.value,
            allow_comments=content.allow_comments,
            active=content.active,
            created_at=content.created_at,
            published_at=content.published_at,
            location_id=content.location_id,
            categories=[],
            hashtags=hashtags
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=ContentListResponse,
    summary="Listar contenidos del usuario",
    description="""
    **Listado de Contenidos del Usuario (HU006)**
    
    Obtiene una lista paginada de todos los contenidos creados por el usuario autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de consulta:**
    - **skip**: Número de registros a omitir (para paginación). Valor por defecto: 0
    - **limit**: Número máximo de registros a retornar. Rango: 1-100. Valor por defecto: 20
    
    **Respuesta:**
    - Lista de contenidos del usuario con toda su información
    - Total de contenidos del usuario
    - Información de paginación (página actual, tamaño de página)
    
    **Uso típico:**
    - Mostrar el perfil de contenido del usuario
    - Dashboard de gestión de contenidos
    - Listado de publicaciones propias
    """,
    response_description="Lista paginada de contenidos del usuario autenticado"
)
async def get_user_contents(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar (1-100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    
    contents = content_service.get_user_contents(current_user.user_id, skip, limit)
    
    content_responses = []
    for content in contents:
        hashtags = []
        if content.hashtags:
            hashtags = [ch.hashtag.name for ch in content.hashtags]
        
        content_responses.append(ContentResponse(
            content_id=content.content_id,
            merchant_id=content.merchant_id,
            merchant_name=current_user.name,
            content_type=content.content_type.value,
            url=content.url,
            title=content.title,
            description=content.description,
            thumbnail_url=content.thumbnail_url,
            duration=content.duration,
            format=content.format,
            resolution=content.resolution,
            visibility=content.visibility.value,
            allow_comments=content.allow_comments,
            active=content.active,
            created_at=content.created_at,
            published_at=content.published_at,
            location_id=content.location_id,
            categories=[],
            hashtags=hashtags
        ))
    
    return ContentListResponse(
        contents=content_responses,
        total=len(content_responses),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Obtener contenido por ID",
    description="""
    **Consulta de Contenido por ID (HU006)**
    
    Obtiene la información detallada de un contenido específico por su ID.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **content_id**: ID único del contenido a consultar
    
    **Comportamiento:**
    - Retorna toda la información del contenido incluyendo metadatos, hashtags, categorías, etc.
    - Si el contenido es privado, solo el propietario puede acceder
    - Si el contenido es público, cualquier usuario autenticado puede verlo
    
    **Errores:**
    - 404: Si el contenido no existe
    - 403: Si intenta acceder a un contenido privado que no le pertenece
    """,
    response_description="Información completa del contenido solicitado"
)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    
    content = content_service.get_content(content_id)
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check visibility
    if content.visibility.value == "private" and content.merchant_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this content"
        )
    
    hashtags = [ch.hashtag.name for ch in content.hashtags] if hasattr(content, 'hashtags') else []
    
    return ContentResponse(
        content_id=content.content_id,
        merchant_id=content.merchant_id,
        merchant_name=content.merchant.name if content.merchant else None,
        content_type=content.content_type.value,
        url=content.url,
        title=content.title,
        description=content.description,
        thumbnail_url=content.thumbnail_url,
        duration=content.duration,
        format=content.format,
        resolution=content.resolution,
        visibility=content.visibility.value,
        allow_comments=content.allow_comments,
        active=content.active,
        created_at=content.created_at,
        published_at=content.published_at,
        location_id=content.location_id,
        categories=[],
        hashtags=hashtags
    )


@router.put(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Actualizar contenido",
    description="""
    **Actualización de Contenido (HU006)**
    
    Permite actualizar la información de un contenido existente.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Permisos:**
    - Solo el propietario del contenido puede actualizarlo
    
    **Parámetros de ruta:**
    - **content_id**: ID único del contenido a actualizar
    
    **Parámetros opcionales (solo se actualizan los campos proporcionados):**
    - **title**: Nuevo título del contenido
    - **description**: Nueva descripción
    - **url**: Nueva URL del contenido
    - **thumbnail_url**: Nueva URL de miniatura
    - **visibility**: Nueva visibilidad (public/private)
    - **allow_comments**: Permitir o no comentarios
    - **location_id**: Nueva ubicación
    - **category_ids**: Nuevas categorías
    - **hashtags**: Nuevos hashtags
    - **scheduled_publish_at**: Nueva fecha de publicación programada
    - **target_audience**: Nueva descripción de audiencia objetivo
    
    **Comportamiento:**
    - Solo actualiza los campos proporcionados en la solicitud
    - Los hashtags y categorías se reemplazan completamente si se proporcionan
    - Si se actualiza la fecha programada, el contenido se reprograma automáticamente
    
    **Errores:**
    - 404: Si el contenido no existe
    - 403: Si no es el propietario del contenido
    """,
    response_description="Contenido actualizado con los nuevos valores"
)
async def update_content(
    content_id: int,
    content_data: ContentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    
    try:
        content = content_service.update_content(content_id, current_user.user_id, content_data)
        
        hashtags = []
        if content.hashtags:
            hashtags = [ch.hashtag.name for ch in content.hashtags]
        
        return ContentResponse(
            content_id=content.content_id,
            merchant_id=content.merchant_id,
            merchant_name=current_user.name,
            content_type=content.content_type.value,
            url=content.url,
            title=content.title,
            description=content.description,
            thumbnail_url=content.thumbnail_url,
            duration=content.duration,
            format=content.format,
            resolution=content.resolution,
            visibility=content.visibility.value,
            allow_comments=content.allow_comments,
            active=content.active,
            created_at=content.created_at,
            published_at=content.published_at,
            location_id=content.location_id,
            categories=[],
            hashtags=hashtags
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar contenido",
    description="""
    **Eliminación de Contenido (HU006)**
    
    Permite eliminar un contenido del sistema. La eliminación es "soft delete", es decir, el contenido se marca como inactivo pero no se elimina físicamente de la base de datos.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Permisos:**
    - Solo el propietario del contenido puede eliminarlo
    
    **Parámetros de ruta:**
    - **content_id**: ID único del contenido a eliminar
    
    **Comportamiento:**
    - Marca el contenido como inactivo (soft delete)
    - El contenido deja de ser visible públicamente
    - Los datos se mantienen en la base de datos para auditoría
    - No se puede recuperar el contenido después de eliminarlo (requiere implementación de restauración)
    
    **Errores:**
    - 404: Si el contenido no existe
    - 403: Si no es el propietario del contenido
    - 400: Si el contenido ya está eliminado
    
    **Nota:** Esta operación no se puede deshacer fácilmente. Asegúrese de querer eliminar el contenido antes de ejecutar esta acción.
    """,
    response_description="Contenido eliminado exitosamente (sin cuerpo de respuesta)"
)
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    
    try:
        content_service.delete_content(content_id, current_user.user_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

