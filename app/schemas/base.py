"""
Schemas base y utilidades comunes
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """Schema base con configuración común"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResponse(BaseSchema):
    """Schema para respuestas de mensajes simples"""
    message: str


class HealthResponse(BaseSchema):
    """Schema para respuestas de health check"""
    status: str
    timestamp: datetime

