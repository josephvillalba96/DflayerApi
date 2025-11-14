"""
Admin User Management Schemas
Schemas for administrative user type management
"""
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import BaseSchema


class ChangeUserTypeRequest(BaseModel):
    """
    Schema for admin to change user type
    
    Permite a un administrador cambiar el tipo de usuario de cualquier usuario,
    incluyendo crear nuevos administradores.
    """
    user_id: int = Field(..., description="ID del usuario cuyo tipo se va a cambiar")
    new_user_type: str = Field(
        ...,
        pattern="^(client|merchant|affiliate|admin)$",
        description="Nuevo tipo de usuario: 'client', 'merchant', 'affiliate', o 'admin'"
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón del cambio de tipo de usuario (para auditoría)"
    )


class ChangeUserTypeResponse(BaseSchema):
    """Schema for user type change response"""
    user_id: int
    previous_user_type: str
    new_user_type: str
    changed_by: int  # Admin user_id
    message: str


class RejectUpgradeRequest(BaseModel):
    """Schema for rejecting an upgrade request"""
    rejection_reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón del rechazo de la solicitud"
    )


class UserUpgradeListResponse(BaseSchema):
    """Schema for listing upgrade requests"""
    upgrade_requests: list[dict]
    total: int
    pending_count: int
    approved_count: int
    rejected_count: int

