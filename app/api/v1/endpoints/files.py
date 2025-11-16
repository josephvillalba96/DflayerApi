"""
File Management Endpoints
Handles file operations with S3: upload, download, delete, and metadata
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.s3_service import S3Service
from app.services.upload_service import UploadService
from app.schemas.base import BaseSchema


router = APIRouter()


# Schemas para respuestas
class FileUploadResponse(BaseSchema):
    """Schema for file upload response"""
    url: str
    s3_key: str
    message: str


class FileMetadataResponse(BaseSchema):
    """Schema for file metadata response"""
    s3_key: str
    size: int
    content_type: str
    last_modified: Optional[str] = None
    etag: Optional[str] = None
    metadata: dict = {}


class FileListResponse(BaseSchema):
    """Schema for file list response"""
    files: List[str]
    prefix: str
    total: int


class PresignedURLResponse(BaseSchema):
    """Schema for presigned URL response"""
    url: str
    s3_key: str
    expiration_seconds: int


# Endpoints de S3

@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir archivo a S3",
    description="""
    **Subir Archivo a S3**
    
    Permite subir un archivo directamente a S3.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **file**: Archivo a subir (form-data)
    - **s3_key**: Ruta/clave del archivo en S3 (query parameter, opcional)
      - Si no se proporciona, se genera automáticamente basado en el tipo de archivo
    - **content_type**: Tipo MIME del archivo (query parameter, opcional)
      - Se detecta automáticamente si no se proporciona
    - **acl**: Control de acceso (query parameter, opcional)
      - Valores: "private" (por defecto), "public-read", "public-read-write"
    
    **Ejemplo de s3_key:**
    - `profile_pictures/user_123.jpg`
    - `content/videos/video_456.mp4`
    - `documents/user_789.pdf`
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    - Si hay error al subir, retorna 500
    """,
    response_description="URL del archivo subido a S3"
)
async def upload_file_to_s3(
    file: UploadFile = File(...),
    s3_key: Optional[str] = Query(None, description="Ruta/clave del archivo en S3"),
    content_type: Optional[str] = Query(None, description="Tipo MIME del archivo"),
    acl: str = Query("private", description="Control de acceso (private, public-read, public-read-write)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Generar s3_key si no se proporciona
        if not s3_key:
            import uuid
            from pathlib import Path
            file_extension = Path(file.filename).suffix if file.filename else ""
            s3_key = f"uploads/{current_user.user_id}/{uuid.uuid4().hex}{file_extension}"
        
        # Determinar content_type
        if not content_type:
            content_type = file.content_type or "application/octet-stream"
        
        # Subir a S3
        url = s3_service.upload_file(
            file_content=file_content,
            s3_key=s3_key,
            content_type=content_type,
            acl=acl
        )
        
        return FileUploadResponse(
            url=url,
            s3_key=s3_key,
            message="File uploaded successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get(
    "/download/{s3_key:path}",
    summary="Descargar archivo de S3",
    description="""
    **Descargar Archivo de S3**
    
    Permite descargar un archivo de S3.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **s3_key**: Ruta/clave del archivo en S3 (path parameter)
      - Ejemplo: `profile_pictures/user_123.jpg`
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    - Si el archivo no existe, retorna 404
    - Si hay error al descargar, retorna 500
    """,
    response_description="Contenido del archivo"
)
async def download_file_from_s3(
    s3_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        # Descargar archivo
        file_content = s3_service.download_file(s3_key)
        
        # Obtener metadatos para content_type
        try:
            metadata = s3_service.get_file_metadata(s3_key)
            content_type = metadata.get("content_type", "application/octet-stream")
        except:
            content_type = "application/octet-stream"
        
        # Retornar archivo como respuesta
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{s3_key.split("/")[-1]}"'
            }
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {s3_key}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )


@router.delete(
    "/delete/{s3_key:path}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar archivo de S3",
    description="""
    **Eliminar Archivo de S3**
    
    Permite eliminar un archivo de S3.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **s3_key**: Ruta/clave del archivo en S3 (path parameter)
      - Ejemplo: `profile_pictures/user_123.jpg`
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    - Si hay error al eliminar, retorna 500
    """,
    response_description="Confirmación de eliminación"
)
async def delete_file_from_s3(
    s3_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        deleted = s3_service.delete_file(s3_key)
        
        if deleted:
            return {"message": f"File deleted successfully: {s3_key}", "deleted": True}
        else:
            return {"message": f"File not found or already deleted: {s3_key}", "deleted": False}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get(
    "/metadata/{s3_key:path}",
    response_model=FileMetadataResponse,
    summary="Obtener metadatos de archivo en S3",
    description="""
    **Obtener Metadatos de Archivo en S3**
    
    Obtiene los metadatos de un archivo almacenado en S3.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **s3_key**: Ruta/clave del archivo en S3 (path parameter)
    
    **Respuesta incluye:**
    - Tamaño del archivo
    - Tipo MIME
    - Fecha de última modificación
    - ETag
    - Metadatos personalizados
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    - Si el archivo no existe, retorna 404
    """,
    response_description="Metadatos del archivo"
)
async def get_file_metadata(
    s3_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        metadata = s3_service.get_file_metadata(s3_key)
        
        return FileMetadataResponse(
            s3_key=s3_key,
            size=metadata.get("size", 0),
            content_type=metadata.get("content_type", "application/octet-stream"),
            last_modified=str(metadata.get("last_modified", "")),
            etag=metadata.get("etag", ""),
            metadata=metadata.get("metadata", {})
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {s3_key}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file metadata: {str(e)}"
        )


@router.get(
    "/exists/{s3_key:path}",
    summary="Verificar si archivo existe en S3",
    description="""
    **Verificar Existencia de Archivo en S3**
    
    Verifica si un archivo existe en S3.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **s3_key**: Ruta/clave del archivo en S3 (path parameter)
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    """,
    response_description="Estado de existencia del archivo"
)
async def check_file_exists(
    s3_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        exists = s3_service.file_exists(s3_key)
        return {"s3_key": s3_key, "exists": exists}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking file existence: {str(e)}"
        )


@router.get(
    "/list",
    response_model=FileListResponse,
    summary="Listar archivos en S3",
    description="""
    **Listar Archivos en S3**
    
    Lista archivos en S3 con un prefijo específico.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de query:**
    - **prefix**: Prefijo para filtrar archivos (opcional)
      - Ejemplo: `profile_pictures/` para listar solo fotos de perfil
    - **max_keys**: Número máximo de archivos a retornar (por defecto 1000)
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    """,
    response_description="Lista de archivos"
)
async def list_files(
    prefix: Optional[str] = Query("", description="Prefijo para filtrar archivos"),
    max_keys: int = Query(1000, description="Número máximo de archivos a retornar"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    try:
        files = s3_service.list_files(prefix=prefix, max_keys=max_keys)
        
        return FileListResponse(
            files=files,
            prefix=prefix,
            total=len(files)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )


@router.get(
    "/presigned-url/{s3_key:path}",
    response_model=PresignedURLResponse,
    summary="Generar URL firmada temporal",
    description="""
    **Generar URL Firmada Temporal (Presigned URL)**
    
    Genera una URL firmada para acceso temporal a un archivo en S3.
    Útil para compartir archivos privados sin exponer credenciales.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de ruta:**
    - **s3_key**: Ruta/clave del archivo en S3 (path parameter)
    
    **Parámetros de query:**
    - **expiration**: Tiempo de expiración en segundos (por defecto 3600 = 1 hora)
    - **http_method**: Método HTTP permitido (GET por defecto, puede ser PUT)
    
    **Errores:**
    - Si S3 no está configurado, retorna 503
    """,
    response_description="URL firmada temporal"
)
async def generate_presigned_url(
    s3_key: str,
    expiration: int = Query(3600, description="Tiempo de expiración en segundos"),
    http_method: str = Query("GET", description="Método HTTP permitido (GET, PUT)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_service = S3Service()
    
    if not s3_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured. Please configure AWS credentials and bucket name."
        )
    
    if http_method not in ["GET", "PUT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="http_method must be 'GET' or 'PUT'"
        )
    
    try:
        url = s3_service.generate_presigned_url(
            s3_key=s3_key,
            expiration=expiration,
            http_method=http_method
        )
        
        return PresignedURLResponse(
            url=url,
            s3_key=s3_key,
            expiration_seconds=expiration
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating presigned URL: {str(e)}"
        )

