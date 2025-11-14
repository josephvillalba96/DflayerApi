"""
Endpoints relacionados con comercios
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get(
    "/",
    summary="Listar comercios",
    description="""
    **Listado de Comercios (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Funcionalidad planificada:**
    - Listar todos los comercios registrados en el sistema
    - Filtros por categoría, ubicación, estado
    - Búsqueda por nombre o descripción
    - Información de comercios asociados a usuarios tipo "merchant"
    
    **Nota:** Los comercios se asocian a usuarios con tipo "merchant" durante el registro.
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def listar_comercios():
    return {"message": "Endpoint de comercios - En desarrollo"}


@router.get(
    "/{comercio_id}",
    summary="Obtener comercio por ID",
    description="""
    **Consulta de Comercio por ID (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Funcionalidad planificada:**
    - Obtener información detallada de un comercio específico
    - Incluir datos del propietario, contenido asociado, estadísticas, etc.
    
    **Parámetros de ruta:**
    - **comercio_id**: ID único del comercio a consultar
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def obtener_comercio(comercio_id: int):
    return {"message": f"Obtener comercio {comercio_id} - En desarrollo"}


@router.post(
    "/",
    summary="Crear comercio",
    description="""
    **Creación de Comercio (En Desarrollo)**
    
    Este endpoint está en desarrollo y actualmente retorna un mensaje indicando que la funcionalidad no está disponible.
    
    **Funcionalidad planificada:**
    - Crear un nuevo comercio asociado a un usuario tipo "merchant"
    - Configurar información del comercio (nombre, descripción, categoría, etc.)
    - Establecer datos de contacto y ubicación
    
    **Nota:** Los comercios se crean automáticamente cuando un usuario se registra con tipo "merchant".
    """,
    response_description="Mensaje indicando que el endpoint está en desarrollo"
)
async def crear_comercio():
    return {"message": "Crear comercio - En desarrollo"}

