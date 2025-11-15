"""
Servicio de Feed Personalizado (HU007)

Este servicio genera feeds de contenido personalizados para usuarios:
- Algoritmo de recomendación basado en intereses del usuario
- Múltiples algoritmos: recommended, following, trending, recent
- Cálculo de scores de relevancia y engagement
- Filtros por categoría y ubicación
- Paginación para scroll infinito

Historia de Usuario: HU007 (Feed Principal)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from app.models.content import Content, Visibility, ContentType
from app.models.user import User
# UserPreferences, UserCategory removed - not in spec
from app.models.follow import Follow
from app.models.like import Like
from app.models.comment import Comment


class FeedService:
    """
    Servicio de Generación de Feed Personalizado
    
    Genera feeds de contenido personalizados usando diferentes algoritmos de recomendación.
    Considera los intereses del usuario, usuarios seguidos, engagement y recencia.
    
    Algoritmos disponibles:
    - recommended: Basado en intereses del usuario (categorías)
    - following: Solo contenido de usuarios seguidos
    - trending: Ordenado por engagement (views, likes, comentarios, shares)
    - recent: Ordenado por fecha de publicación (más reciente primero)
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de feed
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Optional[dict]:
        """
        NOTA: UserPreferences model removed - not in spec
        Returns default preferences
        """
        return {
            "algorithm_preference": "recommended",
            "push_notifications": True,
            "email_notifications": True
        }
    
    def get_user_interests(self, user_id: int) -> List[int]:
        """
        NOTA: UserCategory model removed - not in spec
        Returns empty list
        """
        return []
    
    def get_followed_users(self, user_id: int) -> List[int]:
        """
        Obtiene la lista de IDs de usuarios que el usuario actual sigue
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Lista de IDs de usuarios seguidos
        """
        follows = self.db.query(Follow).filter(
            Follow.follower_id == user_id
        ).all()
        return [f.followed_id for f in follows]
    
    def calculate_relevance_score(
        self,
        content: Content,
        user_interests: List[int],
        content_categories: List[int]
    ) -> float:
        """
        Calcula el score de relevancia de un contenido basado en los intereses del usuario
        
        Factores considerados:
        - Coincidencias de categorías con intereses del usuario (10 puntos por coincidencia)
        - Boost por recencia (hasta 3.5 puntos para contenido del último día)
        - Boost por engagement (likes y comentarios, hasta 10 puntos totales)
        
        Args:
            content: Objeto Content a evaluar
            user_interests: Lista de IDs de categorías de interés del usuario
            content_categories: Lista de IDs de categorías del contenido
        
        Returns:
            Score de relevancia (mayor = más relevante para el usuario)
        """
        score = 0.0
        
        # Check if content categories match user interests
        if user_interests and content_categories:
            matching_categories = set(user_interests) & set(content_categories)
            if matching_categories:
                # Base score for matching categories
                score += len(matching_categories) * 10.0
        
        # Boost for recent content (within last 7 days)
        if content.published_at:
            try:
                if isinstance(content.published_at, datetime):
                    published_date = content.published_at.date()
                else:
                    published_date = content.published_at
                days_old = (datetime.utcnow().date() - published_date).days
                if days_old <= 7:
                    score += (7 - days_old) * 0.5
            except (TypeError, AttributeError):
                pass
        
        # Boost for content with engagement
        if content.metrics:
            if content.metrics.likes_count > 0:
                score += min(content.metrics.likes_count * 0.1, 5.0)
            if content.metrics.comments_count > 0:
                score += min(content.metrics.comments_count * 0.2, 5.0)
        
        return score
    
    def calculate_engagement_score(self, content: Content) -> float:
        """
        Calcula el score de engagement de un contenido para el algoritmo trending
        
        Factores considerados:
        - Views: 0.1 puntos por view
        - Likes: 2.0 puntos por like
        - Comentarios: 3.0 puntos por comentario
        - Shares: 5.0 puntos por share
        - Boost de recencia:
          - 2x para contenido del último día
          - 1.5x para contenido de la última semana
          - 1.2x para contenido del último mes
        
        Args:
            content: Objeto Content a evaluar
        
        Returns:
            Score de engagement (mayor = más popular/engaging)
        """
        if not content.metrics:
            return 0.0
        
        metrics = content.metrics
        
        # Base engagement metrics
        engagement = (
            metrics.views * 0.1 +
            metrics.likes_count * 2.0 +
            metrics.comments_count * 3.0 +
            metrics.shares_count * 5.0
        )
        
        # Recency boost (more recent = higher score)
        if content.published_at:
            try:
                if isinstance(content.published_at, datetime):
                    published_date = content.published_at.date()
                else:
                    published_date = content.published_at
                days_old = (datetime.utcnow().date() - published_date).days
                if days_old <= 1:
                    engagement *= 2.0
                elif days_old <= 7:
                    engagement *= 1.5
                elif days_old <= 30:
                    engagement *= 1.2
            except (TypeError, AttributeError):
                pass
        
        return engagement
    
    def get_feed(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
        algorithm: str = "recommended"
    ) -> Tuple[List[Content], int, str]:
        """
        Obtiene un feed personalizado para el usuario (HU007)
        
        Genera un feed de contenido usando el algoritmo especificado, aplicando
        filtros opcionales y paginación. Respeta las preferencias del usuario
        si están configuradas.
        
        Algoritmos:
        - recommended: Ordena por relevancia basada en intereses del usuario
        - following: Solo contenido de usuarios seguidos (fallback a recommended si no sigue a nadie)
        - trending: Ordena por score de engagement
        - recent: Ordena por fecha de publicación (más reciente primero)
        
        Args:
            user_id: ID del usuario que solicita el feed
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a retornar (1-100)
            category_id: (Opcional) Filtrar contenido por categoría específica
            location_id: (Opcional) Filtrar contenido por ubicación específica
            algorithm: Algoritmo a usar (recommended, following, trending, recent)
        
        Returns:
            Tupla con:
            - Lista de objetos Content ordenados según el algoritmo
            - Total de contenidos disponibles (antes de paginación)
            - Algoritmo utilizado (puede diferir del solicitado si hay fallback)
        """
        # Get user preferences
        preferences = self.get_user_preferences(user_id)
        if preferences and preferences.get("algorithm_preference"):
            algorithm = preferences["algorithm_preference"]
        
        # Base query: only public, active, and published content
        now_utc = datetime.now(timezone.utc)
        query = self.db.query(Content).filter(
            Content.visibility == Visibility.PUBLIC,
            Content.active == True,
            Content.published_at.isnot(None),
            Content.published_at <= now_utc
        )
        
        # Apply filters
        # Note: Category filtering removed as categories are not in the spec
        # Location filtering removed as location is VARCHAR, not FK
        if location_id:
            # Location is now VARCHAR, so we can't filter by location_id
            # If needed, implement text-based location filtering
            pass
        
        # Apply algorithm-specific logic
        if algorithm == "following":
            # Show content from users that the current user follows
            followed_users = self.get_followed_users(user_id)
            if followed_users:
                query = query.filter(Content.merchant_id.in_(followed_users))
            else:
                # If user doesn't follow anyone, fall back to recommended
                algorithm = "recommended"
        
        if algorithm == "trending":
            # Order by engagement score using denormalized counters
            # Metrics are in CONTENT_POSTS (view_count, like_count, etc.)
            query = query.order_by(
                desc(Content.view_count + Content.like_count * 2 + Content.comment_count * 3 + Content.share_count * 5),
                desc(Content.published_at)
            )
        
        elif algorithm == "recent":
            # Order by publication date (newest first)
            query = query.order_by(desc(Content.published_at))
        
        elif algorithm == "recommended":
            # Order by publication date initially, we'll sort by relevance after
            query = query.order_by(desc(Content.published_at))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        contents = query.offset(skip).limit(limit).all()
        
        # Apply algorithm-specific sorting
        if algorithm == "recommended":
            # Get user interests
            user_interests = self.get_user_interests(user_id)
            
            # Calculate relevance scores and sort
            contents_with_scores = []
            for content in contents:
                # Note: Categories removed from spec, using user interests only
                relevance = self.calculate_relevance_score(
                    content,
                    user_interests,
                    []  # No content categories
                )
                contents_with_scores.append((content, relevance))
            
            # Sort by relevance score (descending)
            contents_with_scores.sort(key=lambda x: x[1], reverse=True)
            contents = [c[0] for c in contents_with_scores]
        
        elif algorithm == "trending":
            # Calculate engagement scores and sort
            contents_with_scores = []
            for content in contents:
                engagement = self.calculate_engagement_score(content)
                contents_with_scores.append((content, engagement))
            
            # Sort by engagement score (descending)
            contents_with_scores.sort(key=lambda x: x[1], reverse=True)
            contents = [c[0] for c in contents_with_scores]
        
        return contents, total, algorithm
    
    def get_feed_with_metadata(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
        algorithm: str = "recommended"
    ) -> Tuple[List[dict], int, str]:
        """
        Obtiene un feed personalizado con metadatos adicionales (HU007)
        
        Similar a get_feed(), pero incluye información adicional para cada contenido:
        - Score de relevancia (para algoritmo recommended)
        - Estado de seguimiento del creador (si el usuario sigue al creador)
        - Score de engagement (para algoritmo trending)
        
        Args:
            user_id: ID del usuario que solicita el feed
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a retornar (1-100)
            category_id: (Opcional) Filtrar contenido por categoría específica
            location_id: (Opcional) Filtrar contenido por ubicación específica
            algorithm: Algoritmo a usar (recommended, following, trending, recent)
        
        Returns:
            Tupla con:
            - Lista de diccionarios, cada uno contiene:
              - content: Objeto Content
              - relevance_score: Score de relevancia (si algoritmo es recommended)
              - is_following_creator: True si el usuario sigue al creador
              - engagement_score: Score de engagement (si algoritmo es trending)
            - Total de contenidos disponibles (antes de paginación)
            - Algoritmo utilizado
        
        Nota: Este método es usado por los endpoints para proporcionar información
        adicional útil para el frontend (por ejemplo, mostrar si sigues al creador).
        """
        contents, total, algorithm_used = self.get_feed(
            user_id, skip, limit, category_id, location_id, algorithm
        )
        
        # Get user interests and followed users for metadata
        user_interests = self.get_user_interests(user_id)
        followed_users = set(self.get_followed_users(user_id))
        
        # Build response with metadata
        feed_items = []
        for content in contents:
            # Get content categories (if implemented)
            content_categories = []  # TODO: Implement content-category relationship
            
            # Calculate relevance score
            relevance_score = None
            if algorithm_used == "recommended":
                relevance_score = self.calculate_relevance_score(
                    content, user_interests, content_categories
                )
            
            # Check if following creator
            is_following_creator = content.merchant_id in followed_users
            
            # Calculate engagement score
            engagement_score = None
            if algorithm_used == "trending":
                engagement_score = self.calculate_engagement_score(content)
            
            feed_items.append({
                "content": content,
                "relevance_score": relevance_score,
                "is_following_creator": is_following_creator,
                "engagement_score": engagement_score
            })
        
        return feed_items, total, algorithm_used

