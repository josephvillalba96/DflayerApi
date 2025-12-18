"""
Upload Service (HU004)
Handles file uploads for profile pictures and other user files
Supports both local storage and S3
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
import logging
from app.core.config import settings
from app.services.s3_service import S3Service

logger = logging.getLogger(__name__)


class UploadService:
    """
    Servicio de Upload de Archivos (HU004)
    
    Proporciona métodos para gestionar la subida de archivos:
    - Validación de tamaño (máximo 5MB para fotos de perfil)
    - Validación de tipo de archivo (solo imágenes)
    - Almacenamiento local o en S3 (si está configurado)
    - Generación de URLs de acceso
    """
    
    # Tamaño máximo para fotos de perfil (HU004: max 5MB)
    MAX_PROFILE_PICTURE_SIZE = 5 * 1024 * 1024  # 5MB en bytes
    
    # Tipos MIME permitidos para imágenes
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp"
    }
    
    # Directorio base para uploads locales
    UPLOAD_DIR = Path("uploads")
    PROFILE_PICTURES_DIR = UPLOAD_DIR / "profile_pictures"
    
    def __init__(self):
        """Inicializa el servicio de upload"""
        # Crear directorios si no existen (para almacenamiento local)
        self.PROFILE_PICTURES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Inicializar servicio S3
        self.s3_service = S3Service()
        self.use_s3 = self.s3_service.is_configured()
        
        if self.use_s3:
            logger.info("Upload service initialized with S3 storage")
        else:
            logger.info("Upload service initialized with local storage")
    
    def validate_image_file(self, file: UploadFile) -> None:
        """
        Valida que el archivo sea una imagen válida
        
        Args:
            file: Archivo a validar
        
        Raises:
            HTTPException: Si el archivo no es válido
        """
        # Validar tipo MIME
        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(self.ALLOWED_IMAGE_TYPES)}"
            )
        
        # Validar tamaño (leer contenido para verificar)
        file_content = file.file.read()
        file.file.seek(0)  # Resetear posición del archivo
        
        if len(file_content) > self.MAX_PROFILE_PICTURE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo es demasiado grande. Tamaño máximo: {self.MAX_PROFILE_PICTURE_SIZE / (1024 * 1024):.1f}MB"
            )
        
        # Validar que sea una imagen válida usando PIL
        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()  # Verificar que sea una imagen válida
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo no es una imagen válida: {str(e)}"
            )
    
    def upload_profile_picture(self, file: UploadFile, user_id: int) -> str:
        """
        Sube una foto de perfil para un usuario (HU004)
        
        Args:
            file: Archivo de imagen a subir
            user_id: ID del usuario
        
        Returns:
            URL o ruta del archivo subido
        
        Raises:
            HTTPException: Si el archivo no es válido o hay error en la subida
        """
        # Validar archivo
        self.validate_image_file(file)
        
        # Generar nombre único para el archivo
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = self.PROFILE_PICTURES_DIR / unique_filename
        
        # Leer contenido del archivo
        file_content = file.file.read()
        
        # Determinar tipo MIME
        content_type = file.content_type or "application/octet-stream"
        
        # Generar clave S3
        s3_key = f"profile_pictures/{unique_filename}"
        
        # Subir a S3 si está configurado, sino guardar localmente
        if self.use_s3:
            try:
                # Subir a S3 (siempre como private, acceso a través de la API)
                self.s3_service.upload_file(
                    file_content=file_content,
                    s3_key=s3_key,
                    content_type=content_type,
                    acl="private"  # Siempre privado, acceso solo a través de la API
                )
                logger.info(f"Profile picture uploaded to S3: {s3_key}")
                
                # Generar URL basada en la API usando BASE_URL
                from urllib.parse import quote
                base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
                base_url = base_url.rstrip('/')
                encoded_s3_key = quote(s3_key, safe='')
                url = f"{base_url}{settings.API_V1_STR}/files/{encoded_s3_key}"
                
                return url
            except Exception as e:
                logger.error(f"Error uploading to S3, falling back to local storage: {str(e)}")
                # Fallback a almacenamiento local si S3 falla
                self.use_s3 = False
        
        # Almacenamiento local (fallback o si S3 no está configurado)
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Profile picture saved locally: {file_path}")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el archivo: {str(e)}"
            )
        
        # Generar URL local
        if settings.DEBUG:
            url = f"/uploads/profile_pictures/{unique_filename}"
        else:
            # En producción, usar URL absoluta si está configurado
            base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
            url = f"{base_url}/uploads/profile_pictures/{unique_filename}"
        
        return url
    
    def delete_profile_picture(self, file_url: str) -> bool:
        """
        Elimina una foto de perfil del sistema (S3 o local)
        
        Args:
            file_url: URL o ruta del archivo a eliminar
                    Puede ser una URL de la API: {BASE_URL}/api/v1/files/{s3_key}
                    O una ruta local: /uploads/profile_pictures/filename
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            from urllib.parse import unquote
            
            # Determinar si es una URL de la API (nueva forma)
            if self.use_s3 and f"{settings.API_V1_STR}/files/" in file_url:
                # Extraer s3_key de la URL de la API: {BASE_URL}/api/v1/files/{s3_key}
                try:
                    # Dividir por "/api/v1/files/" o "/files/" y tomar lo que sigue
                    if f"{settings.API_V1_STR}/files/" in file_url:
                        parts = file_url.split(f"{settings.API_V1_STR}/files/")
                    else:
                        parts = file_url.split("/files/")
                    if len(parts) > 1:
                        s3_key = unquote(parts[1])  # Decodificar URL-encoding
                        
                        # Eliminar de S3
                        try:
                            self.s3_service.delete_file(s3_key)
                            logger.info(f"Profile picture deleted from S3: {s3_key}")
                            return True
                        except Exception as e:
                            logger.error(f"Error deleting from S3: {str(e)}")
                            return False
                except Exception as e:
                    logger.error(f"Error parsing API URL: {str(e)}")
            
            # Fallback: Intentar extraer s3_key de URLs de S3 directas (legacy)
            if self.use_s3 and ("s3.amazonaws.com" in file_url or 
                               (settings.AWS_S3_ENDPOINT_URL and settings.AWS_S3_ENDPOINT_URL in file_url)):
                # Extraer s3_key de la URL
                if "s3.amazonaws.com" in file_url:
                    # AWS S3 estándar: https://bucket.s3.region.amazonaws.com/key
                    parts = file_url.split(".s3.")[1].split(".amazonaws.com/")
                    s3_key = parts[1] if len(parts) > 1 else file_url.split("/")[-1]
                elif settings.AWS_S3_ENDPOINT_URL:
                    # S3-compatible: https://endpoint/bucket/key
                    s3_key = file_url.replace(f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_S3_BUCKET_NAME}/", "")
                else:
                    # Intentar extraer de cualquier URL
                    s3_key = "/".join(file_url.split("/")[-2:])  # profile_pictures/filename
                
                # Eliminar de S3
                try:
                    self.s3_service.delete_file(s3_key)
                    logger.info(f"Profile picture deleted from S3: {s3_key}")
                    return True
                except Exception as e:
                    logger.error(f"Error deleting from S3: {str(e)}")
                    return False
            
            # Eliminar archivo local
            if file_url.startswith("/uploads/"):
                file_path = Path(file_url.lstrip("/"))
            elif "profile_pictures" in file_url:
                filename = file_url.split("/")[-1]
                file_path = self.PROFILE_PICTURES_DIR / filename
            else:
                # URL externa desconocida - no se puede eliminar
                logger.warning(f"Cannot determine storage type for URL: {file_url}")
                return False
            
            # Eliminar archivo local si existe
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Profile picture deleted locally: {file_path}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting profile picture: {str(e)}")
            return False

