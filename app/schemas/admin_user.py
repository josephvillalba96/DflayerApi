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
    
    NOTA: Solo existen 2 tipos: 'usuario' y 'admin'.
    Todos los usuarios tienen las mismas funcionalidades.
    """
    user_id: int = Field(..., description="ID del usuario cuyo tipo se va a cambiar")
    new_user_type: str = Field(
        ...,
        pattern="^(usuario|admin)$",
        description="Nuevo tipo de usuario: 'usuario' o 'admin'"
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón del cambio de tipo de usuario (para auditoría)"
    )


class PromoteRequest(BaseModel):
    """
    Schema for promotion requests
    
    Esquema genérico para solicitudes de promoción de usuarios.
    """
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón de la promoción (para auditoría)"
    )


class ChangeUserTypeResponse(BaseSchema):
    """Schema for user type change response"""
    user_id: int
    previous_user_type: str
    new_user_type: str
    changed_by: int  # Admin user_id
    message: str


