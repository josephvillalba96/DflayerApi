"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    **API REST para el proyecto Multiplux - Plataforma de monetización de contenido**
    
    ## Descripción General
    
    Esta API proporciona los endpoints necesarios para gestionar usuarios, contenido, transacciones y monetización en la plataforma Multiplux.
    
    ## Características Principales
    
    ### Autenticación y Seguridad (HU001, HU002)
    - Registro de usuarios con verificación de email
    - Inicio de sesión con autenticación de dos factores (2FA)
    - Restablecimiento de contraseña
    - Gestión de sesiones con JWT
    
    ### Gestión de Datos Fiscales (HU005)
    - Creación y actualización de información fiscal
    - Cálculo automático de retenciones
    - Historial de cambios fiscales
    
    ### Gestión de Contenido (HU006)
    - Creación de contenido multimedia (videos, imágenes, audio, texto)
    - Gestión de hashtags y categorías
    - Programación de publicaciones
    - Control de visibilidad y comentarios
    
    ### Otros Servicios
    - Verificación de salud del sistema
    - Gestión de usuarios y comercios (en desarrollo)
    
    ## Autenticación
    
    La mayoría de los endpoints requieren autenticación mediante JWT. Para obtener un token:
    
    1. Registre un nuevo usuario en `/api/v1/auth/register`
    2. O inicie sesión en `/api/v1/auth/login`
    3. En Swagger UI, haga clic en el botón "Authorize" (🔒) e ingrese: `Bearer <token>`
       O simplemente ingrese el token directamente en el campo de autorización
    
    ## Documentación
    
    - **Swagger UI**: Disponible en `/docs` (interactivo)
    - **ReDoc**: Disponible en `/redoc` (documentación alternativa)
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Configurar esquema de seguridad para Swagger
def custom_openapi():
    """Personaliza el esquema OpenAPI para autenticación simple con token"""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Configurar esquema de seguridad HTTP Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingrese el token JWT obtenido del endpoint /api/v1/auth/login o /api/v1/auth/register. Formato: Bearer <token> o simplemente <token>"
        }
    }
    
    # Aplicar seguridad a todos los endpoints que requieren autenticación
    # (se aplica automáticamente por HTTPBearer en los endpoints)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a DflayerApi",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_version": settings.API_V1_STR,
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud de la API"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

