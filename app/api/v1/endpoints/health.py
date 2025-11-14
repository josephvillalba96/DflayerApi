"""
Endpoints de verificación de salud del sistema
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health():
    """Verificación básica de salud"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/detailed")
async def health_detailed():
    """Verificación detallada de salud con información del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DflayerApi",
        "version": "0.1.0",
    }

