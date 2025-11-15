"""
Admin Log Model (ADMIN_LOGS)
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class AdminLog(Base):
    """Admin log model (ADMIN_LOGS)"""
    __tablename__ = "admin_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action_type = Column(String(100), nullable=False)  # VARCHAR
    entity_type = Column(String(100), nullable=True)  # VARCHAR
    entity_id = Column(String(100), nullable=True)  # VARCHAR
    changes = Column(Text, nullable=True)  # JSON con cambios realizados
    ip_address = Column(String(45), nullable=True)  # IPv4 o IPv6
    user_agent = Column(String(500), nullable=True)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    admin_user = relationship("User", back_populates="admin_logs")

