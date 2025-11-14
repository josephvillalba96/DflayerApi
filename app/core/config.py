"""
Configuración de la aplicación usando Pydantic Settings
"""
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información del proyecto
    PROJECT_NAME: str = "DflayerApi"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Base de datos
    DATABASE_URL: Optional[str] = None
    
    # CORS - puede ser string separado por comas o lista
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    # Configuración del servidor
    DEBUG: bool = True
    
    # SendGrid (Email)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: Optional[str] = None
    SENDGRID_FROM_NAME: Optional[str] = None
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET_NAME: Optional[str] = None
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    
    # Transcoding (Optional)
    TRANSCODING_WORKER_COUNT: int = 4
    TRANSCODING_MAX_RETRIES: int = 3
    TRANSCODING_QUEUE_SIZE: int = 100
    FFMPEG_PATH: Optional[str] = None
    FFPROBE_PATH: Optional[str] = None
    
    # Frontend URL (for email links)
    FRONTEND_URL: Optional[str] = None
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if isinstance(v, list) else []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

