"""
Email Verification Model
Modelo para almacenar tokens de verificación de email (HU001)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.models.base import Base


class EmailVerification(Base):
    """
    Modelo para tokens de verificación de email
    
    Almacena tokens de verificación enviados por email para validar
    la dirección de correo electrónico del usuario.
    
    HU001: Confirmación de código dentro de 10 minutos
    """
    __tablename__ = "email_verifications"

    verification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", backref="email_verifications")

    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Verifica si el token es válido (no expirado y no verificado)"""
        return not self.verified and not self.is_expired()

