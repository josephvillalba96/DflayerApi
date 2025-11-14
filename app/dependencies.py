"""
Dependencias comunes de FastAPI
"""
from typing import Generator
from app.db.base import get_db
from sqlalchemy.orm import Session

# Re-exportar get_db para uso en endpoints
__all__ = ["get_db"]

