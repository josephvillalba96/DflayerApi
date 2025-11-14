"""
Endpoints de verificación de salud del sistema
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get(
    "/",
    summary="Verificación básica de salud",
    description="""
    **Verificación Básica de Salud del Sistema**
    
    Endpoint simple para verificar que el servicio está funcionando correctamente.
    
    **Sin autenticación requerida**
    
    **Respuesta:**
    - **status**: Estado del servicio (siempre "healthy" si el servicio está activo)
    - **timestamp**: Fecha y hora actual en formato ISO 8601
    
    **Uso típico:**
    - Health checks de load balancers
    - Monitoreo básico del servicio
    - Verificación rápida de disponibilidad
    """,
    response_description="Estado básico de salud del servicio"
)
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/detailed",
    summary="Verificación detallada de salud",
    description="""
    **Verificación Detallada de Salud del Sistema**
    
    Endpoint extendido que proporciona información adicional sobre el estado del servicio.
    
    **Sin autenticación requerida**
    
    **Respuesta:**
    - **status**: Estado del servicio (siempre "healthy" si el servicio está activo)
    - **timestamp**: Fecha y hora actual en formato ISO 8601
    - **service**: Nombre del servicio (DflayerApi)
    - **version**: Versión actual de la API
    
    **Uso típico:**
    - Monitoreo detallado del servicio
    - Verificación de versión en despliegues
    - Dashboard de estado del sistema
    """,
    response_description="Estado detallado de salud del servicio con información adicional"
)
async def health_detailed():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DflayerApi",
        "version": "0.1.0",
    }

