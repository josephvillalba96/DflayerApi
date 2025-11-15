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
    InterestCategoriesListResponse
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
    - **biography**: Nueva biografía (máximo 500 caracteres)
    - **birth_date**: Nueva fecha de nacimiento (formato YYYY-MM-DD)
    - **location_id**: ID de la nueva ubicación
    
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
            location_id=updated_user.location_id,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names
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
    
    Permite al usuario autenticado actualizar su foto de perfil.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **profile_picture_url**: URL de la foto de perfil (máximo 500 caracteres)
    
    **Nota:** La URL debe apuntar a una imagen válida. El sistema no valida la existencia de la imagen,
    pero se recomienda usar URLs de servicios de almacenamiento confiables (S3, CDN, etc.).
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
            location_id=updated_user.location_id,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names
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
    
    Permite al usuario autenticado actualizar su foto de portada.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **cover_picture_url**: URL de la foto de portada (máximo 500 caracteres)
    
    **Nota:** La URL debe apuntar a una imagen válida. El sistema no valida la existencia de la imagen,
    pero se recomienda usar URLs de servicios de almacenamiento confiables (S3, CDN, etc.).
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
            location_id=updated_user.location_id,
            level=updated_user.level,
            verified=updated_user.verified,
            following_count=updated_user.following_count,
            followers_count=updated_user.followers_count,
            registration_date=updated_user.registration_date,
            interest_categories=interest_names
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Obtener perfil completo del usuario",
    description="""
    **Consulta de Perfil Completo (HU004)**
    
    Obtiene toda la información del perfil del usuario autenticado, incluyendo:
    - Información personal (nombre, biografía, fecha de nacimiento)
    - Fotos de perfil y portada
    - Categorías de interés
    - Estadísticas (seguidores, seguidos, nivel)
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    """,
    response_description="Perfil completo del usuario autenticado"
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
        location_id=user.location_id,
        level=user.level,
        verified=user.verified,
        following_count=user.following_count,
        followers_count=user.followers_count,
        registration_date=user.registration_date,
        interest_categories=interest_names
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
        user_category = user_service.add_interest_category(
            current_user.user_id,
            interest_data.category_id
        )
        
        # Get category name
        from app.models.category import Category
        category = db.query(Category).filter(
            Category.category_id == interest_data.category_id
        ).first()
        
        return InterestCategoryResponse(
            category_id=category.category_id,
            category_name=category.name,
            added_at=datetime.utcnow()
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

