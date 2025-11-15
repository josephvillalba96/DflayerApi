"""
SMS Verification Model
Modelo para almacenar códigos de verificación SMS (HU001)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.models.base import Base


class SMSVerification(Base):
    """
    Modelo para códigos de verificación SMS
    
    Almacena códigos de verificación enviados por SMS para validar
    el número de teléfono del usuario.
    
    HU001: Envío de código de verificación por SMS o email
    HU001: Confirmación de código dentro de 10 minutos
    """
    __tablename__ = "sms_verifications"

    verification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    code = Column(String(6), nullable=False)  # Código de 6 dígitos
    expires_at = Column(DateTime, nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)  # Intentos de verificación
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", backref="sms_verifications")

    def is_expired(self) -> bool:
        """Verifica si el código ha expirado"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Verifica si el código es válido (no expirado y no verificado)"""
        return not self.verified and not self.is_expired() and self.attempts < 5

