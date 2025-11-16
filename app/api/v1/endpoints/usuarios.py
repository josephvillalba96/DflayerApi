"""
Endpoints relacionados con usuarios (HU004)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import (
    ProfileUpdateRequest,
    ProfilePictureUpdateRequest,
    CoverPictureUpdateRequest,
    UserProfileResponse,
    InterestCategoryRequest,
    InterestCategoryResponse,
    InterestCategoriesListResponse,
    BusinessAccountActivateRequest,
    BusinessAccountDeactivateRequest,
    BusinessAccountResponse
)

router = APIRouter()


# HU004 - Completar Perfil de Usuario

@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Actualizar perfil de usuario",
    description="""
    **Actualización de Perfil de Usuario (HU004)**
    
    Permite al usuario autenticado actualizar su información personal:
    - Nombre completo
    - Biografía
    - Fecha de nacimiento
    - Ubicación
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros opcionales (solo se actualizan los campos proporcionados):**
    - **name**: Nuevo nombre completo
    - **biography**: Nueva biografía (máximo 150 caracteres según HU004)
    - **birth_date**: Nueva fecha de nacimiento (formato YYYY-MM-DD)
    - **city**: Ciudad
    - **country**: País
    
    **Nota:** Todos los campos son opcionales. Solo se actualizan los campos que se proporcionan.
    """,
    response_description="Perfil del usuario actualizado"
)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_profile(current_user.user_id, profile_data)
        
        # Get interest categories
        interests = user_service.get_user_interests(updated_user.user_id)
        interest_names = [i["category_name"] for i in interests]
        
        return UserProfileResponse(
            user_id=updated_user.user_id,
            name=updated_user.name,
            username=updated_user.username,
            email=updated_user.email,
            biography=updated_user.biography,
            profile_picture=updated_user.profile_picture,
            cover_picture=updated_user.cover_picture,
            birth_date=updated_user.birth_date,
            city=updated_user.city,
            country=updated_user.country,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names,
            is_business_account=updated_user.is_business_account,
            business_name=updated_user.business_name,
            business_category=updated_user.business_category
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/me/profile-picture",
    response_model=UserProfileResponse,
    summary="Actualizar foto de perfil",
    description="""
    **Actualización de Foto de Perfil (HU004)**
    
    Permite al usuario autenticado actualizar su foto de perfil proporcionando una URL.
    
    **IMPORTANTE - Flujo de trabajo:**
    1. Primero, sube el archivo usando el endpoint de S3: **POST /api/v1/files/upload**
    2. Obtén la URL del archivo subido desde la respuesta
    3. Usa esa URL en este endpoint para actualizar la foto de perfil
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **profile_picture_url**: URL de la foto de perfil generada por el servicio de S3
      - Esta URL debe ser obtenida del endpoint `/api/v1/files/upload`
      - Máximo 500 caracteres
    
    **Ejemplo de flujo:**
    1. `POST /api/v1/files/upload` con el archivo → retorna `{"url": "https://...", "s3_key": "..."}`
    2. `PUT /api/v1/usuarios/me/profile-picture` con `{"profile_picture_url": "https://..."}`
    
    **Nota:** Este endpoint NO acepta archivos directamente. Debe usar los servicios de S3 para subir archivos.
    """,
    response_description="Perfil del usuario con foto de perfil actualizada"
)
async def update_profile_picture(
    picture_data: ProfilePictureUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_profile_picture(current_user.user_id, picture_data)
        
        # Get interest categories
        interests = user_service.get_user_interests(updated_user.user_id)
        interest_names = [i["category_name"] for i in interests]
        
        return UserProfileResponse(
            user_id=updated_user.user_id,
            name=updated_user.name,
            username=updated_user.username,
            email=updated_user.email,
            biography=updated_user.biography,
            profile_picture=updated_user.profile_picture,
            cover_picture=updated_user.cover_picture,
            birth_date=updated_user.birth_date,
            city=updated_user.city,
            country=updated_user.country,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names,
            is_business_account=updated_user.is_business_account,
            business_name=updated_user.business_name,
            business_category=updated_user.business_category
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/me/cover-picture",
    response_model=UserProfileResponse,
    summary="Actualizar foto de portada",
    description="""
    **Actualización de Foto de Portada (HU004)**
    
    Permite al usuario autenticado actualizar su foto de portada proporcionando una URL.
    
    **IMPORTANTE - Flujo de trabajo:**
    1. Primero, sube el archivo usando el endpoint de S3: **POST /api/v1/files/upload**
    2. Obtén la URL del archivo subido desde la respuesta
    3. Usa esa URL en este endpoint para actualizar la foto de portada
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **cover_picture_url**: URL de la foto de portada generada por el servicio de S3
      - Esta URL debe ser obtenida del endpoint `/api/v1/files/upload`
      - Máximo 500 caracteres
    
    **Ejemplo de flujo:**
    1. `POST /api/v1/files/upload` con el archivo → retorna `{"url": "https://...", "s3_key": "..."}`
    2. `PUT /api/v1/usuarios/me/cover-picture` con `{"cover_picture_url": "https://..."}`
    
    **Nota:** Este endpoint NO acepta archivos directamente. Debe usar los servicios de S3 para subir archivos.
    """,
    response_description="Perfil del usuario con foto de portada actualizada"
)
async def update_cover_picture(
    picture_data: CoverPictureUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_cover_picture(current_user.user_id, picture_data)
        
        # Get interest categories
        interests = user_service.get_user_interests(updated_user.user_id)
        interest_names = [i["category_name"] for i in interests]
        
        return UserProfileResponse(
            user_id=updated_user.user_id,
            name=updated_user.name,
            username=updated_user.username,
            email=updated_user.email,
            biography=updated_user.biography,
            profile_picture=updated_user.profile_picture,
            cover_picture=updated_user.cover_picture,
            birth_date=updated_user.birth_date,
            city=updated_user.city,
            country=updated_user.country,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names,
            is_business_account=updated_user.is_business_account,
            business_name=updated_user.business_name,
            business_category=updated_user.business_category
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Vista previa del perfil",
    description="""
    **Vista Previa del Perfil (HU004)**
    
    Obtiene toda la información del perfil del usuario autenticado para vista previa, incluyendo:
    - Información personal (nombre, biografía, fecha de nacimiento)
    - Ubicación (ciudad/país)
    - Fotos de perfil y portada
    - Categorías de interés
    - Estadísticas (seguidores, seguidos, nivel)
    - Información de cuenta de negocio (si está activa)
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Nota:** Este endpoint proporciona una vista previa completa del perfil tal como se verá
    para otros usuarios (con la información pública visible).
    """,
    response_description="Vista previa completa del perfil del usuario autenticado"
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    user = user_service.get_user_profile(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get interest categories
    interests = user_service.get_user_interests(user.user_id)
    interest_names = [i["category_name"] for i in interests]
    
    return UserProfileResponse(
        user_id=user.user_id,
        name=user.name,
        username=user.username,
        email=user.email,
        biography=user.biography,
        profile_picture=user.profile_picture,
        cover_picture=user.cover_picture,
        birth_date=user.birth_date,
        city=user.city,
        country=user.country,
        level=user.level,
        verified=user.verified,
        following_count=user.following_count,
        followers_count=user.followers_count,
        registration_date=user.registration_date,
        interest_categories=interest_names,
        is_business_account=user.is_business_account,
        business_name=user.business_name,
        business_category=user.business_category
    )


# Gestión de Categorías de Interés

@router.get(
    "/me/interests",
    response_model=InterestCategoriesListResponse,
    summary="Obtener categorías de interés del usuario",
    description="""
    **Consulta de Categorías de Interés (HU004)**
    
    Obtiene todas las categorías de interés asociadas al usuario autenticado.
    Estas categorías se utilizan para personalizar el feed y las recomendaciones.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    """,
    response_description="Lista de categorías de interés del usuario"
)
async def get_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    interests = user_service.get_user_interests(current_user.user_id)
    
    categories = [
        InterestCategoryResponse(
            category_id=i["category_id"],
            category_name=i["category_name"],
            added_at=datetime.utcnow()  # TODO: Add created_at to UserCategory model
        )
        for i in interests
    ]
    
    return InterestCategoriesListResponse(
        categories=categories,
        total=len(categories)
    )


@router.post(
    "/me/interests",
    response_model=InterestCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar categoría de interés",
    description="""
    **Agregar Categoría de Interés (HU004)**
    
    Permite al usuario autenticado agregar una categoría a sus intereses.
    Las categorías de interés se utilizan para personalizar el feed y las recomendaciones.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **category_id**: ID de la categoría a agregar
    
    **Errores:**
    - Si la categoría no existe, retorna 400
    - Si la categoría ya está en los intereses del usuario, retorna 400
    """,
    response_description="Categoría de interés agregada exitosamente"
)
async def add_interest(
    interest_data: InterestCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        # NOTA: Las categorías de interés están deshabilitadas porque el modelo UserCategory
        # no está en el documento ANÁLISIS COMPLETO DEL.txt
        user_service.add_interest_category(
            current_user.user_id,
            interest_data.category_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/me/interests/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría de interés",
    description="""
    **Eliminar Categoría de Interés (HU004)**
    
    Permite al usuario autenticado eliminar una categoría de sus intereses.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **category_id**: ID de la categoría a eliminar
    
    **Errores:**
    - Si la categoría no está en los intereses del usuario, retorna 400
    """,
    response_description="Categoría eliminada exitosamente (sin contenido en respuesta)"
)
async def remove_interest(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        user_service.remove_interest_category(current_user.user_id, category_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# HU-003: Activar cuenta de negocio

@router.post(
    "/me/business-account/activate",
    response_model=BusinessAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar cuenta de negocio",
    description="""
    **Activar Cuenta de Negocio (HU003)**
    
    Permite al usuario autenticado convertir su cuenta personal en cuenta de negocio.
    
    **IMPORTANTE - ACLARACIÓN CRÍTICA:**
    - Esta funcionalidad es **OPCIONAL** - se puede usar la plataforma sin activar esto
    - **NO otorga funcionalidades adicionales**
    - Cualquier usuario YA puede crear campañas, vender bonos, etc., sin necesidad de activar cuenta de negocio
    - Es solo una **distinción de presentación/branding**
    - Se puede desactivar en cualquier momento
    - Un influencer personal puede crear campañas SIN ser cuenta de negocio
    
    **Cambios visuales en perfil:**
    - Badge de "Negocio"
    - Muestra nombre comercial prominente
    - Categoría visible
    - Dashboard con terminología comercial
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **business_name**: Nombre comercial o de marca (2-200 caracteres)
    - **business_category**: Categoría de negocio (2-100 caracteres)
    
    **Parámetros opcionales:**
    - **tax_data_id**: ID de datos fiscales empresariales (opcional)
      - Si se proporciona, debe existir y pertenecer al usuario
      - Si no se proporciona, el usuario puede agregarlo después
    
    **Errores:**
    - Si el usuario no existe, retorna 400
    - Si los datos fiscales no existen o no pertenecen al usuario, retorna 400
    
    **Nota:** Esta es una funcionalidad de baja prioridad (cosmética, no funcional).
    """,
    response_description="Cuenta de negocio activada exitosamente"
)
async def activate_business_account(
    business_data: BusinessAccountActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    try:
        updated_user = user_service.activate_business_account(
            current_user.user_id,
            business_data
        )
        
        return BusinessAccountResponse(
            user_id=updated_user.user_id,
            is_business_account=updated_user.is_business_account,
            business_name=updated_user.business_name,
            business_category=updated_user.business_category,
            tax_data_id=updated_user.tax_data_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/me/business-account/deactivate",
    response_model=BusinessAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Desactivar cuenta de negocio",
    description="""
    **Desactivar Cuenta de Negocio (HU003)**
    
    Permite al usuario autenticado convertir su cuenta de negocio de vuelta a cuenta personal.
    Esto solo afecta la presentación visual del perfil.
    
    **IMPORTANTE:**
    - Los datos de negocio (business_name, business_category) se mantienen en la base de datos
    - Se pueden reactivar en cualquier momento sin perder la información
    - NO afecta las funcionalidades del usuario (ya que no otorgaba funcionalidades adicionales)
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **confirm**: Confirmación para desactivar cuenta de negocio (por defecto: true)
    
    **Errores:**
    - Si el usuario no existe, retorna 400
    """,
    response_description="Cuenta de negocio desactivada exitosamente"
)
async def deactivate_business_account(
    deactivate_data: BusinessAccountDeactivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not deactivate_data.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required to deactivate business account"
        )
    
    user_service = UserService(db)
    
    try:
        updated_user = user_service.deactivate_business_account(current_user.user_id)
        
        return BusinessAccountResponse(
            user_id=updated_user.user_id,
            is_business_account=updated_user.is_business_account,
            business_name=updated_user.business_name,
            business_category=updated_user.business_category,
            tax_data_id=updated_user.tax_data_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me/business-account",
    response_model=BusinessAccountResponse,
    summary="Obtener información de cuenta de negocio",
    description="""
    **Consulta de Información de Cuenta de Negocio (HU003)**
    
    Obtiene la información de cuenta de negocio del usuario autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Respuesta:**
    - **is_business_account**: Indica si la cuenta de negocio está activa
    - **business_name**: Nombre comercial (solo visible si is_business_account = true)
    - **business_category**: Categoría de negocio (solo visible si is_business_account = true)
    - **tax_data_id**: ID de datos fiscales empresariales (opcional)
    """,
    response_description="Información de cuenta de negocio del usuario"
)
async def get_business_account_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    user = user_service.get_business_account_info(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return BusinessAccountResponse(
        user_id=user.user_id,
        is_business_account=user.is_business_account,
        business_name=user.business_name,
        business_category=user.business_category,
        tax_data_id=user.tax_data_id
    )

