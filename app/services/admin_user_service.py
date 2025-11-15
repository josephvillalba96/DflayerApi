"""
Admin User Service
Handles administrative operations for user type management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.user import User, UserType
from app.schemas.admin_user import ChangeUserTypeRequest


class AdminUserService:
    """
    Servicio Administrativo de Gestión de Usuarios
    
    Proporciona métodos para que los administradores gestionen tipos de usuario.
    Solo usuarios con tipo 'admin' pueden cambiar tipos de usuario.
    
    NOTA: Solo existen 2 tipos de usuario: 'admin' y 'usuario'.
    Todos los usuarios tienen las mismas funcionalidades (crear contenido, campañas, bonos).
    is_business_account es solo visual, no funcional.
    
    Características:
    - Cambiar tipo de usuario de cualquier usuario (solo admin)
    - Crear nuevos administradores (solo admin, a partir de cualquier usuario)
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio administrativo de usuarios
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def change_user_type(
        self,
        target_user_id: int,
        new_user_type: str,
        admin_user_id: int,
        reason: Optional[str] = None
    ) -> User:
        """
        Cambia el tipo de usuario de cualquier usuario (Solo admin)
        
        Puede cambiar cualquier usuario a 'usuario' o 'admin'.
        Solo admin puede cambiar tipos de usuario.
        
        Args:
            target_user_id: ID del usuario cuyo tipo se va a cambiar
            new_user_type: Nuevo tipo de usuario ('usuario', 'admin')
            admin_user_id: ID del administrador que realiza el cambio
            reason: Razón del cambio (opcional, para auditoría)
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si el usuario objetivo no existe, el admin no es admin,
                       o el nuevo tipo de usuario es inválido
        """
        # Verify admin user
        admin = self.db.query(User).filter(User.user_id == admin_user_id).first()
        if not admin or admin.user_type != UserType.ADMIN:
            raise ValueError("Only administrators can change user types")
        
        # Prevent self-demotion (admin cannot change their own type)
        if target_user_id == admin_user_id:
            raise ValueError("Administrators cannot change their own user type")
        
        # Get target user
        target_user = self.db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            raise ValueError("Target user not found")
        
        # Validate new user type
        try:
            new_type = UserType[new_user_type.upper()] if new_user_type.upper() == "ADMIN" else UserType.USER
        except (KeyError, AttributeError):
            # Handle "usuario" as USER
            if new_user_type.lower() in ["usuario", "user"]:
                new_type = UserType.USER
            elif new_user_type.lower() == "admin":
                new_type = UserType.ADMIN
            else:
                raise ValueError(
                    f"Invalid user_type. Must be one of: {', '.join([t.value for t in UserType])}"
                )
        
        # Update user type
        target_user.user_type = new_type
        
        self.db.commit()
        self.db.refresh(target_user)
        
        return target_user
    
    def create_admin(
        self,
        user_id: int,
        admin_id: int,
        reason: Optional[str] = None
    ) -> User:
        """
        Crea un nuevo administrador a partir de cualquier usuario (Solo admin)
        
        Método específico para crear administradores. Solo admin puede ejecutar esta acción.
        
        Args:
            user_id: ID del usuario a convertir en administrador
            admin_id: ID del administrador que realiza la acción
            reason: Razón de la promoción (opcional, para auditoría)
        
        Returns:
            Objeto User actualizado con tipo 'admin'
        
        Raises:
            ValueError: Si el usuario no existe o el admin no es válido
        """
        return self.change_user_type(
            target_user_id=user_id,
            new_user_type="admin",
            admin_user_id=admin_id,
            reason=reason
        )

