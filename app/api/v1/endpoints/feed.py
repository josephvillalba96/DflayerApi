"""
Feed Endpoints (HU007)
Handles personalized content feed with recommendation algorithm
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.feed_service import FeedService
from app.schemas.feed import FeedRequest, FeedResponse, FeedItemResponse
from app.schemas.content import ContentResponse

router = APIRouter()


@router.get(
    "",
    response_model=FeedResponse,
    summary="Obtener feed personalizado",
    description="""
    **Feed Principal Personalizado (HU007)**
    
    Obtiene un feed personalizado de contenido basado en las preferencias e intereses del usuario.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros de consulta:**
    - **skip**: Número de registros a omitir (para paginación). Valor por defecto: 0
    - **limit**: Número máximo de registros a retornar. Rango: 1-100. Valor por defecto: 20
    - **category_id**: (Opcional) Filtrar contenido por categoría específica
    - **location_id**: (Opcional) Filtrar contenido por ubicación específica
    - **algorithm**: Algoritmo de recomendación a usar. Valores permitidos:
      - `recommended` (por defecto): Basado en intereses del usuario
      - `following`: Solo contenido de usuarios que sigues
      - `trending`: Contenido más popular por engagement
      - `recent`: Contenido más reciente primero
    
    **Algoritmos de Recomendación:**
    
    1. **Recommended (Recomendado)**: 
       - Prioriza contenido de categorías que coinciden con los intereses del usuario
       - Considera engagement (likes, comentarios) y recencia
       - Calcula un score de relevancia para cada contenido
    
    2. **Following (Siguiendo)**:
       - Muestra solo contenido de usuarios que el usuario actual sigue
       - Si no sigue a nadie, cae automáticamente a "recommended"
    
    3. **Trending (Tendencia)**:
       - Ordena por score de engagement (views, likes, comentarios, shares)
       - Aplica boost de recencia (contenido reciente tiene mayor peso)
    
    4. **Recent (Reciente)**:
       - Ordena simplemente por fecha de publicación (más reciente primero)
    
    **Scroll Infinito:**
    - Use los parámetros `skip` y `limit` para implementar scroll infinito
    - Incremente `skip` por el valor de `limit` en cada carga adicional
    - El campo `has_more` indica si hay más contenido disponible
    
    **Filtros:**
    - Los filtros por categoría y ubicación se aplican antes del algoritmo de ordenamiento
    - Puede combinar múltiples filtros simultáneamente
    
    **Respuesta:**
    - Lista de contenidos con metadatos adicionales (score de relevancia, si sigues al creador, etc.)
    - Información de paginación
    - Algoritmo utilizado
    """,
    response_description="Feed personalizado con contenido relevante para el usuario"
)
async def get_feed(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar (1-100)"),
    category_id: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    location_id: Optional[int] = Query(None, description="Filtrar por ID de ubicación"),
    algorithm: str = Query("recommended", pattern="^(recommended|following|trending|recent)$", description="Algoritmo de recomendación"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed_service = FeedService(db)
    
    try:
        # Get feed with metadata
        feed_items, total, algorithm_used = feed_service.get_feed_with_metadata(
            user_id=current_user.user_id,
            skip=skip,
            limit=limit,
            category_id=category_id,
            location_id=location_id,
            algorithm=algorithm
        )
        
        # Build response
        items_response = []
        for item in feed_items:
            content = item["content"]
            
            # Get hashtags
            hashtags = []
            if content.hashtags:
                hashtags = [ch.hashtag.name for ch in content.hashtags]
            
            # Build content response
            content_response = ContentResponse(
                content_id=content.content_id,
                merchant_id=content.merchant_id,
                merchant_name=content.merchant.name if content.merchant else None,
                content_type=content.content_type.value,
                url=content.url,
                title=content.title,
                description=content.description,
                thumbnail_url=content.thumbnail_url,
                duration=content.duration,
                format=content.format,
                resolution=content.resolution,
                visibility=content.visibility.value,
                allow_comments=content.allow_comments,
                active=content.active,
                created_at=content.created_at,
                published_at=content.published_at,
                location_id=content.location_id,
                categories=[],  # TODO: Implement content categories
                hashtags=hashtags
            )
            
            # Build feed item response
            feed_item = FeedItemResponse(
                content=content_response,
                relevance_score=item.get("relevance_score"),
                is_following_creator=item.get("is_following_creator"),
                engagement_score=item.get("engagement_score")
            )
            items_response.append(feed_item)
        
        # Calculate pagination
        page = (skip // limit) + 1 if limit > 0 else 1
        has_more = (skip + limit) < total
        
        return FeedResponse(
            items=items_response,
            total=total,
            page=page,
            page_size=limit,
            has_more=has_more,
            algorithm_used=algorithm_used
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating feed: {str(e)}"
        )

