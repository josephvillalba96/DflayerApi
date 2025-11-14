"""
Admin User Service
Handles administrative operations for user type management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.user import User, UserType
from app.models.user_upgrade import UserUpgradeRequest, UpgradeRequestStatus
from app.schemas.admin_user import ChangeUserTypeRequest


class AdminUserService:
    """
    Servicio Administrativo de Gestión de Usuarios
    
    Proporciona métodos para que los administradores gestionen tipos de usuario.
    Solo usuarios con tipo 'admin' pueden usar estos métodos.
    
    Características:
    - Cambiar tipo de usuario de cualquier usuario
    - Crear nuevos administradores (a partir de cualquier tipo de usuario)
    - Aprobar/rechazar solicitudes de upgrade
    - Listar solicitudes de upgrade pendientes
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
        Cambia el tipo de usuario de cualquier usuario (Solo administradores)
        
        Puede cambiar cualquier usuario (client, merchant, affiliate) a cualquier tipo,
        incluyendo crear nuevos administradores.
        
        Args:
            target_user_id: ID del usuario cuyo tipo se va a cambiar
            new_user_type: Nuevo tipo de usuario ('client', 'merchant', 'affiliate', 'admin')
            admin_user_id: ID del administrador que realiza el cambio
            reason: Razón del cambio (opcional, para auditoría)
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si el usuario objetivo no existe, el admin no es válido,
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
            new_type = UserType[new_user_type.upper()]
        except KeyError:
            raise ValueError(
                f"Invalid user_type. Must be one of: {', '.join([t.value for t in UserType])}"
            )
        
        # Store previous type before updating
        previous_type = target_user.user_type.value
        
        # Update user type
        target_user.user_type = new_type
        
        # If there's a pending upgrade request for this user, mark it as processed
        upgrade_request = self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.user_id == target_user_id,
            UserUpgradeRequest.status == UpgradeRequestStatus.PENDING
        ).first()
        
        if upgrade_request:
            # If changing to the requested type, approve it
            if new_type.value == upgrade_request.requested_user_type:
                upgrade_request.status = UpgradeRequestStatus.APPROVED
                upgrade_request.reviewed_by = admin_user_id
                upgrade_request.reviewed_at = datetime.utcnow()
            # Otherwise, reject it
            else:
                upgrade_request.status = UpgradeRequestStatus.REJECTED
                upgrade_request.reviewed_by = admin_user_id
                upgrade_request.reviewed_at = datetime.utcnow()
                upgrade_request.rejection_reason = f"User type changed to {new_type.value} by admin"
        
        self.db.commit()
        self.db.refresh(target_user)
        
        return target_user
    
    def get_all_upgrade_requests(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserUpgradeRequest]:
        """
        Obtiene todas las solicitudes de upgrade (Solo administradores)
        
        Args:
            status: Filtrar por estado ('pending', 'approved', 'rejected'). None para todas
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a retornar
        
        Returns:
            Lista de objetos UserUpgradeRequest
        """
        query = self.db.query(UserUpgradeRequest)
        
        if status:
            try:
                status_enum = UpgradeRequestStatus[status.upper()]
                query = query.filter(UserUpgradeRequest.status == status_enum)
            except KeyError:
                pass
        
        return query.order_by(UserUpgradeRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_upgrade_request(self, upgrade_request_id: int) -> Optional[UserUpgradeRequest]:
        """
        Obtiene una solicitud de upgrade por ID
        
        Args:
            upgrade_request_id: ID de la solicitud
        
        Returns:
            Objeto UserUpgradeRequest si existe, None en caso contrario
        """
        return self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.upgrade_request_id == upgrade_request_id
        ).first()

