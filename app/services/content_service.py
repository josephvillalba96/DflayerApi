"""
Servicio de Contenido (HU006)

Este servicio maneja la creación y gestión de contenido multimedia:
- Creación de publicaciones con multimedia (videos, imágenes, audio, texto)
- Gestión de hashtags y categorías
- Programación de publicaciones
- Control de visibilidad y comentarios
- Soft delete de contenido

Historia de Usuario: HU006 (Crear Publicación)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.content import Content, ContentType, Visibility
from app.models.user import User
from app.models.hashtag import Hashtag, ContentHashtag
from app.models.category import Category
from app.schemas.content import ContentCreateRequest, ContentUpdateRequest


class ContentService:
    """
    Servicio de Gestión de Contenido
    
    Proporciona métodos para crear, actualizar, consultar y eliminar contenido.
    Todos los usuarios autenticados pueden crear contenido (client, merchant, affiliate, admin).
    
    Características:
    - Soporte para múltiples tipos de contenido (video, imagen, audio, texto)
    - Gestión automática de hashtags
    - Programación de publicaciones
    - Control de visibilidad (público/privado)
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de contenido
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def create_content(self, merchant_id: int, content_data: ContentCreateRequest) -> Content:
        """
        Crea una nueva publicación de contenido (HU006)
        
        Todos los usuarios autenticados pueden crear contenido.
        
        Proceso:
        1. Verifica que el usuario existe
        2. Determina la fecha de publicación (inmediata o programada)
        3. Crea el contenido con los metadatos proporcionados
        4. Asocia hashtags automáticamente (crea nuevos si no existen)
        5. Asocia categorías si se proporcionan
        
        Args:
            merchant_id: ID del usuario que crea el contenido
            content_data: Datos del contenido a crear
        
        Returns:
            Objeto Content creado
        
        Raises:
            ValueError: Si el usuario no existe
        
        Nota: El contenido debe subirse primero a un servicio de almacenamiento (S3)
        y luego proporcionar la URL en content_data.url
        """
        # Verify user exists
        user = self.db.query(User).filter(User.user_id == merchant_id).first()
        if not user:
            raise ValueError("User not found")
        
        # All users can create content (client, merchant, affiliate, admin)
        # No restriction on user_type for content creation
        
        # Determine publish date
        published_at = None
        if content_data.scheduled_publish_at:
            if content_data.scheduled_publish_at > datetime.utcnow():
                published_at = content_data.scheduled_publish_at
            else:
                published_at = datetime.utcnow()
        else:
            published_at = datetime.utcnow()
        
        # Create content
        content = Content(
            merchant_id=merchant_id,
            content_type=ContentType[content_data.content_type.upper()],
            url=content_data.url or "",
            title=content_data.title,
            description=content_data.description,
            thumbnail_url=content_data.thumbnail_url,
            visibility=Visibility[content_data.visibility.upper()],
            allow_comments=content_data.allow_comments,
            location_id=content_data.location_id,
            published_at=published_at,
            active=True
        )
        
        self.db.add(content)
        self.db.flush()
        
        # Handle hashtags
        if content_data.hashtags:
            self._add_hashtags(content.content_id, content_data.hashtags)
        
        # Handle categories (if category relationship exists)
        # Note: This would require a ContentCategory join table if not already implemented
        
        self.db.commit()
        self.db.refresh(content)
        
        return content
    
    def _add_hashtags(self, content_id: int, hashtags: List[str]):
        """
        Agrega hashtags a un contenido
        
        Crea los hashtags si no existen y los asocia al contenido.
        Los hashtags se normalizan (se elimina el # y se convierte a minúsculas).
        
        Args:
            content_id: ID del contenido
            hashtags: Lista de hashtags (pueden incluir o no el símbolo #)
        """
        for tag_name in hashtags:
            # Remove # if present
            tag_clean = tag_name.lstrip('#').lower()
            
            # Find or create hashtag
            hashtag = self.db.query(Hashtag).filter(
                Hashtag.name == tag_clean
            ).first()
            
            if not hashtag:
                hashtag = Hashtag(name=tag_clean)
                self.db.add(hashtag)
                self.db.flush()
            
            # Check if relationship already exists
            existing = self.db.query(ContentHashtag).filter(
                ContentHashtag.content_id == content_id,
                ContentHashtag.hashtag_id == hashtag.hashtag_id
            ).first()
            
            if not existing:
                content_hashtag = ContentHashtag(
                    content_id=content_id,
                    hashtag_id=hashtag.hashtag_id
                )
                self.db.add(content_hashtag)
    
    def update_content(self, content_id: int, merchant_id: int, content_data: ContentUpdateRequest) -> Content:
        """
        Actualiza un contenido existente (HU006)
        
        Solo el propietario del contenido puede actualizarlo.
        Solo se actualizan los campos que se proporcionan en la solicitud.
        
        Args:
            content_id: ID del contenido a actualizar
            merchant_id: ID del usuario que solicita la actualización (para autorización)
            content_data: Datos a actualizar (solo los campos proporcionados)
        
        Returns:
            Objeto Content actualizado
        
        Raises:
            ValueError: Si el contenido no existe o el usuario no tiene permisos
        """
        content = self.db.query(Content).filter(Content.content_id == content_id).first()
        if not content:
            raise ValueError("Content not found")
        
        # Verify ownership
        if content.merchant_id != merchant_id:
            raise ValueError("You don't have permission to update this content")
        
        # Update fields
        if content_data.title is not None:
            content.title = content_data.title
        if content_data.description is not None:
            content.description = content_data.description
        if content_data.thumbnail_url is not None:
            content.thumbnail_url = content_data.thumbnail_url
        if content_data.visibility is not None:
            content.visibility = Visibility[content_data.visibility.upper()]
        if content_data.allow_comments is not None:
            content.allow_comments = content_data.allow_comments
        if content_data.active is not None:
            content.active = content_data.active
        
        self.db.commit()
        self.db.refresh(content)
        
        return content
    
    def get_content(self, content_id: int) -> Optional[Content]:
        """
        Obtiene un contenido por su ID
        
        Args:
            content_id: ID del contenido
        
        Returns:
            Objeto Content si existe, None en caso contrario
        """
        return self.db.query(Content).filter(Content.content_id == content_id).first()
    
    def get_user_contents(self, merchant_id: int, skip: int = 0, limit: int = 20) -> List[Content]:
        """
        Obtiene los contenidos de un usuario/comercio con paginación
        
        Args:
            merchant_id: ID del usuario/comercio
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a retornar
        
        Returns:
            Lista de objetos Content del usuario
        """
        return self.db.query(Content).filter(
            Content.merchant_id == merchant_id
        ).offset(skip).limit(limit).all()
    
    def delete_content(self, content_id: int, merchant_id: int) -> bool:
        """
        Elimina un contenido (soft delete) (HU006)
        
        Realiza una eliminación lógica marcando el contenido como inactivo.
        Solo el propietario del contenido puede eliminarlo.
        
        Args:
            content_id: ID del contenido a eliminar
            merchant_id: ID del usuario que solicita la eliminación (para autorización)
        
        Returns:
            True si la eliminación fue exitosa
        
        Raises:
            ValueError: Si el contenido no existe o el usuario no tiene permisos
        
        Nota: El contenido se marca como inactivo pero no se elimina físicamente
        de la base de datos para mantener auditoría.
        """
        content = self.db.query(Content).filter(Content.content_id == content_id).first()
        if not content:
            raise ValueError("Content not found")
        
        if content.merchant_id != merchant_id:
            raise ValueError("You don't have permission to delete this content")
        
        content.active = False
        self.db.commit()
        
        return True


