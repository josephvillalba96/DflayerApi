"""
Password Reset Model
Modelo para almacenar tokens de recuperación de contraseña (HU002)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.models.base import Base


class PasswordReset(Base):
    """
    Modelo para tokens de recuperación de contraseña
    
    Almacena tokens de recuperación enviados por email para permitir
    al usuario restablecer su contraseña en caso de olvido.
    
    HU002: Recuperación de cuenta por correo
    """
    __tablename__ = "password_resets"

    reset_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", backref="password_resets")

    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.used and not self.is_expired()

