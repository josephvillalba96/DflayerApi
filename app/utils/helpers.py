"""
Funciones auxiliares y utilidades generales
"""
from typing import Any, Dict


def format_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Formatea una respuesta estándar de la API"""
    return {
        "message": message,
        "data": data,
    }


def paginate_response(items: list, total: int, page: int, page_size: int) -> Dict[str, Any]:
    """Formatea una respuesta paginada"""
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }

