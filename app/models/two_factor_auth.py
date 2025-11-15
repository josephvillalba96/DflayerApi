"""
Two Factor Authentication Model
Modelo para almacenar configuración de 2FA (HU002)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class TwoFactorAuth(Base):
    """
    Modelo para autenticación de dos factores (2FA)
    
    Almacena la configuración de 2FA para usuarios, incluyendo:
    - Clave secreta TOTP
    - Códigos de respaldo
    - Estado de habilitación
    
    HU002: Opción de habilitar 2FA en configuración
    HU002: Uso de app autenticadora (Google Authenticator, Authy)
    HU002: Códigos de respaldo para recuperación
    """
    __tablename__ = "two_factor_auth"

    two_factor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    secret_key = Column(String(255), nullable=False)  # TOTP secret
    backup_codes = Column(Text, nullable=True)  # JSON array de códigos de respaldo
    enabled = Column(Boolean, default=False, nullable=False)  # Solo se habilita después de verificación
    verified_at = Column(DateTime, nullable=True)  # Fecha de verificación inicial
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", backref="two_factor_auth")

