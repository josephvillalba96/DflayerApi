"""
Bono Purchase Model (BONO_PURCHASES)
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class PurchaseStatus(str, enum.Enum):
    """Enum for purchase status"""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class BonoPurchase(Base):
    """Bono purchase model (BONO_PURCHASES)"""
    __tablename__ = "bono_purchases"

    purchase_id = Column(Integer, primary_key=True, index=True)
    bono_id = Column(Integer, ForeignKey("bonos.bono_id"), nullable=False)
    buyer_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # DECIMAL
    total_amount = Column(Float, nullable=False)  # DECIMAL
    purchase_status = Column(SQLEnum(PurchaseStatus), default=PurchaseStatus.PENDING)
    payment_method = Column(String(100), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    purchased_at = Column(Date, default=datetime.utcnow)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationships
    bono = relationship("Bono", back_populates="purchases")
    buyer = relationship("User", back_populates="bono_purchases")
    codes = relationship("BonoCode", back_populates="purchase")
    sales_commissions = relationship("SalesCommission", back_populates="purchase")

