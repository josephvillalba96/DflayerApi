"""
Router principal de la API v1
Agrupa todos los endpoints de la versión 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, usuarios, comercios

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(comercios.router, prefix="/comercios", tags=["comercios"])

