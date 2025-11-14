"""
User Upgrade Schemas
Schemas for users to request upgrade to merchant or affiliate
"""
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import BaseSchema


class UserUpgradeRequest(BaseModel):
    """
    Schema for user upgrade request (client to merchant/affiliate)
    
    El usuario puede solicitar cambiar su tipo de usuario a merchant o affiliate.
    Esta solicitud debe ser aprobada por un administrador.
    """
    target_user_type: str = Field(
        ...,
        pattern="^(merchant|affiliate)$",
        description="Tipo de usuario objetivo: 'merchant' o 'affiliate'"
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón o justificación para el cambio de tipo de usuario"
    )
    business_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Nombre del negocio (requerido para merchant)"
    )
    business_description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción del negocio o actividad"
    )


class UserUpgradeResponse(BaseSchema):
    """Schema for user upgrade response"""
    upgrade_request_id: Optional[int] = None
    user_id: int
    current_user_type: str
    requested_user_type: str
    status: str  # pending, approved, rejected
    message: str


class UserUpgradeStatusResponse(BaseSchema):
    """Schema for checking upgrade request status"""
    has_pending_request: bool
    current_user_type: str
    requested_user_type: Optional[str] = None
    status: Optional[str] = None  # pending, approved, rejected
    message: Optional[str] = None

