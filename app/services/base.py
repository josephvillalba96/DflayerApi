"""
Clase base para servicios
"""
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Clase base para servicios con operaciones CRUD comunes"""
    
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Obtiene un registro por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtiene todos los registros con paginación"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> ModelType:
        """Crea un nuevo registro"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

