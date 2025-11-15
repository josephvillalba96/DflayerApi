"""
Bono Code Model (BONO_CODES)
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class RedemptionStatus(str, enum.Enum):
    """Enum for redemption status"""
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BonoCode(Base):
    """Bono code model (BONO_CODES)"""
    __tablename__ = "bono_codes"

    code_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("bono_purchases.purchase_id"), nullable=False)
    qr_code = Column(String(255), unique=True, nullable=False, index=True)  # código único
    qr_image_url = Column(String(500), nullable=True)
    redemption_status = Column(SQLEnum(RedemptionStatus), default=RedemptionStatus.ACTIVE)
    redeemed_at = Column(Date, nullable=True)
    redeemed_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # empleado que escaneó
    created_at = Column(Date, default=datetime.utcnow)
    expires_at = Column(Date, nullable=True)

    # Relationships
    purchase = relationship("BonoPurchase", back_populates="codes")
    redeemed_by = relationship("User", foreign_keys=[redeemed_by_user_id], back_populates="bono_codes_redeemed")

