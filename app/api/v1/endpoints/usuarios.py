"""
Endpoints relacionados con usuarios
"""
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get(
    "/",
    summary="Listar usuarios",
    description="""
    **Listado de Usuarios (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Funcionalidad planificada:**
    - Listar todos los usuarios del sistema (con paginación)
    - Filtros por tipo de usuario, nivel, estado de verificación
    - Búsqueda por nombre, email o username
    
    **Nota:** Use el endpoint `/api/v1/auth/register` para crear usuarios y `/api/v1/auth/me` para obtener información del usuario actual.
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def listar_usuarios():
    return {"message": "Endpoint de usuarios - En desarrollo"}


@router.get(
    "/{usuario_id}",
    summary="Obtener usuario por ID",
    description="""
    **Consulta de Usuario por ID (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Funcionalidad planificada:**
    - Obtener información detallada de un usuario específico por su ID
    - Incluir estadísticas, contenido creado, nivel, etc.
    
    **Nota:** Use el endpoint `/api/v1/auth/me` para obtener información del usuario autenticado.
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def obtener_usuario(usuario_id: int):
    return {"message": f"Obtener usuario {usuario_id} - En desarrollo"}


@router.post(
    "/",
    summary="Crear usuario",
    description="""
    **Creación de Usuario (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Nota:** Para crear usuarios, use el endpoint `/api/v1/auth/register` que proporciona registro completo con verificación de email y autenticación.
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def crear_usuario():
    return {"message": "Crear usuario - En desarrollo"}

