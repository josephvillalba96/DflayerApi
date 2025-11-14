"""
Category Service (Administrative)
Handles administrative operations for category management
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.category import Category
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


class CategoryService:
    """
    Servicio Administrativo de Gestión de Categorías
    
    Proporciona métodos para gestionar categorías del sistema.
    Solo usuarios con permisos administrativos pueden usar estos métodos.
    
    Características:
    - Crear nuevas categorías
    - Actualizar categorías existentes
    - Eliminar categorías
    - Listar todas las categorías
    - Consultar categoría por ID
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de categorías
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def create_category(self, category_data: CategoryCreateRequest) -> Category:
        """
        Crea una nueva categoría (Solo administradores)
        
        Args:
            category_data: Datos de la categoría a crear
        
        Returns:
            Objeto Category creado
        
        Raises:
            ValueError: Si el nombre de la categoría ya existe
        """
        # Check if category name already exists
        existing = self.db.query(Category).filter(
            Category.name.ilike(category_data.name)
        ).first()
        
        if existing:
            raise ValueError(f"Category with name '{category_data.name}' already exists")
        
        # Create category
        category = Category(
            name=category_data.name,
            description=category_data.description,
            icon=category_data.icon
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def update_category(self, category_id: int, category_data: CategoryUpdateRequest) -> Category:
        """
        Actualiza una categoría existente (Solo administradores)
        
        Args:
            category_id: ID de la categoría a actualizar
            category_data: Datos a actualizar (solo los campos proporcionados)
        
        Returns:
            Objeto Category actualizado
        
        Raises:
            ValueError: Si la categoría no existe o el nuevo nombre ya está en uso
        """
        category = self.db.query(Category).filter(
            Category.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("Category not found")
        
        # Check if new name conflicts with existing category
        if category_data.name and category_data.name != category.name:
            existing = self.db.query(Category).filter(
                Category.name.ilike(category_data.name),
                Category.category_id != category_id
            ).first()
            
            if existing:
                raise ValueError(f"Category with name '{category_data.name}' already exists")
        
        # Update fields
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description
        if category_data.icon is not None:
            category.icon = category_data.icon
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Obtiene una categoría por su ID
        
        Args:
            category_id: ID de la categoría
        
        Returns:
            Objeto Category si existe, None en caso contrario
        """
        return self.db.query(Category).filter(
            Category.category_id == category_id
        ).first()
    
    def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Obtiene todas las categorías con paginación
        
        Args:
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a retornar
        
        Returns:
            Lista de objetos Category
        """
        return self.db.query(Category).offset(skip).limit(limit).all()
    
    def delete_category(self, category_id: int) -> bool:
        """
        Elimina una categoría (Solo administradores)
        
        Nota: Verificar que la categoría no esté en uso antes de eliminar.
        
        Args:
            category_id: ID de la categoría a eliminar
        
        Returns:
            True si la eliminación fue exitosa
        
        Raises:
            ValueError: Si la categoría no existe o está en uso
        """
        category = self.db.query(Category).filter(
            Category.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("Category not found")
        
        # Check if category is in use (has users associated via UserCategory)
        from app.models.user_preferences import UserCategory
        user_categories_count = self.db.query(UserCategory).filter(
            UserCategory.category_id == category_id
        ).count()
        
        if user_categories_count > 0:
            raise ValueError(
                f"Cannot delete category '{category.name}': it is associated with {user_categories_count} users"
            )
        
        self.db.delete(category)
        self.db.commit()
        
        return True

