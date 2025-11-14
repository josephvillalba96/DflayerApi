"""
Configuración de base de datos y sesión
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear engine (se configurará cuando se defina DATABASE_URL)
engine = None
SessionLocal = None

if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency para obtener sesión de base de datos
    Uso: db: Session = Depends(get_db)
    """
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurada")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

