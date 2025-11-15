"""
Router principal de la API v1
Agrupa todos los endpoints de la versión 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, usuarios, comercios, auth, tax_data, content, feed, admin

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(comercios.router, prefix="/comercios", tags=["comercios"])
api_router.include_router(tax_data.router, prefix="/tax-data", tags=["tax-data"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

