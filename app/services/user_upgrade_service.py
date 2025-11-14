"""
User Upgrade Service
Handles user requests to upgrade from client to merchant or affiliate
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.user import User, UserType
from app.models.user_upgrade import UserUpgradeRequest, UpgradeRequestStatus
from app.schemas.user_upgrade import UserUpgradeRequest as UserUpgradeRequestSchema


class UserUpgradeService:
    """
    Servicio de Solicitud de Cambio de Tipo de Usuario
    
    Permite a los usuarios solicitar cambiar su tipo de usuario de 'client' a 'merchant' o 'affiliate'.
    Las solicitudes deben ser aprobadas por un administrador.
    
    Características:
    - Los usuarios pueden solicitar upgrade a merchant o affiliate
    - Solo usuarios tipo 'client' pueden solicitar upgrade
    - Las solicitudes quedan en estado 'pending' hasta aprobación
    - Solo un administrador puede aprobar o rechazar solicitudes
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de upgrade de usuarios
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def request_upgrade(self, user_id: int, upgrade_data: UserUpgradeRequestSchema) -> UserUpgradeRequest:
        """
        Solicita un cambio de tipo de usuario (client -> merchant/affiliate)
        
        Args:
            user_id: ID del usuario que solicita el upgrade
            upgrade_data: Datos de la solicitud (target_user_type, reason, etc.)
        
        Returns:
            Objeto UserUpgradeRequest creado
        
        Raises:
            ValueError: Si el usuario no existe, no es tipo 'client',
                       ya tiene una solicitud pendiente, o el tipo objetivo es inválido
        """
        # Verify user exists
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Only clients can request upgrade
        if user.user_type != UserType.CLIENT:
            raise ValueError(
                f"Only users with type 'client' can request upgrade. "
                f"Current type: {user.user_type.value}"
            )
        
        # Validate target user type
        if upgrade_data.target_user_type not in ["merchant", "affiliate"]:
            raise ValueError("target_user_type must be 'merchant' or 'affiliate'")
        
        # Check if user already has a pending request
        existing_request = self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.user_id == user_id,
            UserUpgradeRequest.status == UpgradeRequestStatus.PENDING
        ).first()
        
        if existing_request:
            raise ValueError(
                f"You already have a pending upgrade request to '{existing_request.requested_user_type}'"
            )
        
        # Create upgrade request
        upgrade_request = UserUpgradeRequest(
            user_id=user_id,
            current_user_type=user.user_type.value,
            requested_user_type=upgrade_data.target_user_type,
            status=UpgradeRequestStatus.PENDING,
            reason=upgrade_data.reason,
            business_name=upgrade_data.business_name,
            business_description=upgrade_data.business_description
        )
        
        self.db.add(upgrade_request)
        self.db.commit()
        self.db.refresh(upgrade_request)
        
        return upgrade_request
    
    def get_user_upgrade_status(self, user_id: int) -> Optional[UserUpgradeRequest]:
        """
        Obtiene el estado de la solicitud de upgrade de un usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Objeto UserUpgradeRequest si existe, None en caso contrario
        """
        return self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.user_id == user_id
        ).order_by(UserUpgradeRequest.created_at.desc()).first()
    
    def approve_upgrade(self, upgrade_request_id: int, admin_user_id: int) -> User:
        """
        Aprueba una solicitud de upgrade (Solo administradores)
        
        Args:
            upgrade_request_id: ID de la solicitud de upgrade
            admin_user_id: ID del administrador que aprueba
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si la solicitud no existe, ya fue procesada, o el usuario no es admin
        """
        # Verify admin user
        admin = self.db.query(User).filter(User.user_id == admin_user_id).first()
        if not admin or admin.user_type != UserType.ADMIN:
            raise ValueError("Only administrators can approve upgrade requests")
        
        # Get upgrade request
        upgrade_request = self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.upgrade_request_id == upgrade_request_id
        ).first()
        
        if not upgrade_request:
            raise ValueError("Upgrade request not found")
        
        if upgrade_request.status != UpgradeRequestStatus.PENDING:
            raise ValueError(
                f"Upgrade request already processed. Current status: {upgrade_request.status.value}"
            )
        
        # Get user
        user = self.db.query(User).filter(User.user_id == upgrade_request.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update user type
        if upgrade_request.requested_user_type == "merchant":
            user.user_type = UserType.MERCHANT
        elif upgrade_request.requested_user_type == "affiliate":
            user.user_type = UserType.AFFILIATE
        else:
            raise ValueError(f"Invalid requested_user_type: {upgrade_request.requested_user_type}")
        
        # Update upgrade request
        upgrade_request.status = UpgradeRequestStatus.APPROVED
        upgrade_request.reviewed_by = admin_user_id
        upgrade_request.reviewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(upgrade_request)
        
        return user
    
    def reject_upgrade(self, upgrade_request_id: int, admin_user_id: int, rejection_reason: str) -> UserUpgradeRequest:
        """
        Rechaza una solicitud de upgrade (Solo administradores)
        
        Args:
            upgrade_request_id: ID de la solicitud de upgrade
            admin_user_id: ID del administrador que rechaza
            rejection_reason: Razón del rechazo
        
        Returns:
            Objeto UserUpgradeRequest actualizado
        
        Raises:
            ValueError: Si la solicitud no existe, ya fue procesada, o el usuario no es admin
        """
        # Verify admin user
        admin = self.db.query(User).filter(User.user_id == admin_user_id).first()
        if not admin or admin.user_type != UserType.ADMIN:
            raise ValueError("Only administrators can reject upgrade requests")
        
        # Get upgrade request
        upgrade_request = self.db.query(UserUpgradeRequest).filter(
            UserUpgradeRequest.upgrade_request_id == upgrade_request_id
        ).first()
        
        if not upgrade_request:
            raise ValueError("Upgrade request not found")
        
        if upgrade_request.status != UpgradeRequestStatus.PENDING:
            raise ValueError(
                f"Upgrade request already processed. Current status: {upgrade_request.status.value}"
            )
        
        # Update upgrade request
        upgrade_request.status = UpgradeRequestStatus.REJECTED
        upgrade_request.reviewed_by = admin_user_id
        upgrade_request.reviewed_at = datetime.utcnow()
        upgrade_request.rejection_reason = rejection_reason
        
        self.db.commit()
        self.db.refresh(upgrade_request)
        
        return upgrade_request

