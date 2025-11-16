"""
S3 Service
Handles file operations with AWS S3: upload, download, delete, and URL generation
"""
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional, BinaryIO, Dict, List
from pathlib import Path
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """
    Servicio de Gestión de Archivos en S3
    
    Proporciona métodos para gestionar archivos en AWS S3:
    - Cargar archivos a S3
    - Obtener/descargar archivos de S3
    - Borrar archivos de S3
    - Generar URLs firmadas (presigned URLs) para acceso temporal
    - Verificar si un archivo existe
    - Listar archivos en un prefijo
    
    Características:
    - Soporte para S3 estándar y S3-compatible (MinIO, DigitalOcean Spaces, etc.)
    - Manejo robusto de errores
    - Logging de operaciones
    - Validación de configuración
    """
    
    def __init__(self):
        """Inicializa el servicio de S3"""
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_REGION or "us-east-1"
        
        # Verificar si S3 está configurado
        if not self.bucket_name:
            logger.warning("S3 bucket name not configured. S3 operations will fail.")
            self.s3_client = None
            self.s3_resource = None
            return
        
        # Configurar cliente S3
        try:
            s3_config = {
                "region_name": self.region
            }
            
            # Agregar credenciales si están configuradas
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                s3_config["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                s3_config["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            
            # Agregar endpoint personalizado si está configurado (para S3-compatible)
            if settings.AWS_S3_ENDPOINT_URL:
                s3_config["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
            
            self.s3_client = boto3.client("s3", **s3_config)
            self.s3_resource = boto3.resource("s3", **s3_config)
            
            logger.info(f"S3 service initialized. Bucket: {self.bucket_name}, Region: {self.region}")
        except Exception as e:
            logger.error(f"Error initializing S3 service: {str(e)}")
            self.s3_client = None
            self.s3_resource = None
    
    def is_configured(self) -> bool:
        """
        Verifica si S3 está configurado correctamente
        
        Returns:
            True si S3 está configurado, False en caso contrario
        """
        return self.s3_client is not None and self.bucket_name is not None
    
    def upload_file(
        self,
        file_content: bytes,
        s3_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        acl: str = "private"
    ) -> str:
        """
        Carga un archivo a S3
        
        Args:
            file_content: Contenido del archivo en bytes
            s3_key: Ruta/clave del archivo en S3 (ej: "profile_pictures/user_123.jpg")
            content_type: Tipo MIME del archivo (ej: "image/jpeg")
            metadata: Metadatos adicionales para el archivo
            acl: Control de acceso (private, public-read, etc.)
        
        Returns:
            URL del archivo en S3
        
        Raises:
            ValueError: Si S3 no está configurado
            Exception: Si hay error al subir el archivo
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            # Preparar parámetros de upload
            upload_params = {
                "Bucket": self.bucket_name,
                "Key": s3_key,
                "Body": file_content,
                "ACL": acl
            }
            
            if content_type:
                upload_params["ContentType"] = content_type
            
            if metadata:
                upload_params["Metadata"] = metadata
            
            # Subir archivo
            self.s3_client.put_object(**upload_params)
            
            # Generar URL del archivo
            if settings.AWS_S3_ENDPOINT_URL:
                # S3-compatible (MinIO, DigitalOcean Spaces, etc.)
                url = f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"
            else:
                # AWS S3 estándar
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"File uploaded to S3: {s3_key}")
            return url
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"Error uploading file to S3: {error_code} - {str(e)}")
            raise Exception(f"Error uploading file to S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file to S3: {str(e)}")
            raise
    
    def download_file(self, s3_key: str) -> bytes:
        """
        Descarga un archivo de S3
        
        Args:
            s3_key: Ruta/clave del archivo en S3
        
        Returns:
            Contenido del archivo en bytes
        
        Raises:
            ValueError: Si S3 no está configurado
            FileNotFoundError: Si el archivo no existe en S3
            Exception: Si hay error al descargar el archivo
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            file_content = response["Body"].read()
            logger.info(f"File downloaded from S3: {s3_key}")
            return file_content
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                logger.warning(f"File not found in S3: {s3_key}")
                raise FileNotFoundError(f"File not found in S3: {s3_key}")
            logger.error(f"Error downloading file from S3: {error_code} - {str(e)}")
            raise Exception(f"Error downloading file from S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error downloading file from S3: {str(e)}")
            raise
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Elimina un archivo de S3
        
        Args:
            s3_key: Ruta/clave del archivo en S3
        
        Returns:
            True si el archivo fue eliminado, False si no existía
        
        Raises:
            ValueError: Si S3 no está configurado
            Exception: Si hay error al eliminar el archivo
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"File deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                logger.warning(f"File not found in S3 (already deleted?): {s3_key}")
                return False
            logger.error(f"Error deleting file from S3: {error_code} - {str(e)}")
            raise Exception(f"Error deleting file from S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error deleting file from S3: {str(e)}")
            raise
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Verifica si un archivo existe en S3
        
        Args:
            s3_key: Ruta/clave del archivo en S3
        
        Returns:
            True si el archivo existe, False en caso contrario
        
        Raises:
            ValueError: Si S3 no está configurado
            Exception: Si hay error al verificar
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404" or error_code == "NoSuchKey":
                return False
            logger.error(f"Error checking file existence in S3: {error_code} - {str(e)}")
            raise Exception(f"Error checking file existence in S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error checking file existence in S3: {str(e)}")
            raise
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> str:
        """
        Genera una URL firmada (presigned URL) para acceso temporal a un archivo
        
        Args:
            s3_key: Ruta/clave del archivo en S3
            expiration: Tiempo de expiración en segundos (por defecto 1 hora)
            http_method: Método HTTP permitido (GET, PUT, etc.)
        
        Returns:
            URL firmada para acceso temporal
        
        Raises:
            ValueError: Si S3 no está configurado
            Exception: Si hay error al generar la URL
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object" if http_method == "GET" else "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"Presigned URL generated for: {s3_key} (expires in {expiration}s)")
            return url
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"Error generating presigned URL: {error_code} - {str(e)}")
            raise Exception(f"Error generating presigned URL: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            raise
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[str]:
        """
        Lista archivos en S3 con un prefijo específico
        
        Args:
            prefix: Prefijo para filtrar archivos (ej: "profile_pictures/")
            max_keys: Número máximo de archivos a retornar
        
        Returns:
            Lista de claves (s3_key) de los archivos encontrados
        
        Raises:
            ValueError: Si S3 no está configurado
            Exception: Si hay error al listar archivos
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if "Contents" not in response:
                return []
            
            files = [obj["Key"] for obj in response["Contents"]]
            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"Error listing files in S3: {error_code} - {str(e)}")
            raise Exception(f"Error listing files in S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error listing files in S3: {str(e)}")
            raise
    
    def get_file_metadata(self, s3_key: str) -> Dict:
        """
        Obtiene metadatos de un archivo en S3
        
        Args:
            s3_key: Ruta/clave del archivo en S3
        
        Returns:
            Diccionario con metadatos del archivo (tamaño, tipo, fecha de modificación, etc.)
        
        Raises:
            ValueError: Si S3 no está configurado
            FileNotFoundError: Si el archivo no existe
            Exception: Si hay error al obtener metadatos
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            metadata = {
                "size": response.get("ContentLength", 0),
                "content_type": response.get("ContentType", "application/octet-stream"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {})
            }
            
            logger.info(f"Retrieved metadata for: {s3_key}")
            return metadata
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404" or error_code == "NoSuchKey":
                raise FileNotFoundError(f"File not found in S3: {s3_key}")
            logger.error(f"Error getting file metadata from S3: {error_code} - {str(e)}")
            raise Exception(f"Error getting file metadata from S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error getting file metadata from S3: {str(e)}")
            raise
    
    def copy_file(self, source_key: str, destination_key: str) -> str:
        """
        Copia un archivo dentro de S3
        
        Args:
            source_key: Ruta/clave del archivo origen en S3
            destination_key: Ruta/clave del archivo destino en S3
        
        Returns:
            URL del archivo copiado
        
        Raises:
            ValueError: Si S3 no está configurado
            FileNotFoundError: Si el archivo origen no existe
            Exception: Si hay error al copiar el archivo
        """
        if not self.is_configured():
            raise ValueError("S3 is not configured. Please set AWS_S3_BUCKET_NAME and credentials.")
        
        try:
            copy_source = {
                "Bucket": self.bucket_name,
                "Key": source_key
            }
            
            self.s3_resource.Bucket(self.bucket_name).copy(
                copy_source,
                destination_key
            )
            
            # Generar URL del archivo copiado
            if settings.AWS_S3_ENDPOINT_URL:
                url = f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{destination_key}"
            else:
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{destination_key}"
            
            logger.info(f"File copied in S3: {source_key} -> {destination_key}")
            return url
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                raise FileNotFoundError(f"Source file not found in S3: {source_key}")
            logger.error(f"Error copying file in S3: {error_code} - {str(e)}")
            raise Exception(f"Error copying file in S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error copying file in S3: {str(e)}")
            raise

