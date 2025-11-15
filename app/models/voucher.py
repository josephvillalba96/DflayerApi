"""
Bono Model (BONOS)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Bono(Base):
    """Digital voucher model (BONOS)"""
    __tablename__ = "bonos"  # vouchers en legacy

    bono_id = Column(Integer, primary_key=True, index=True)  # voucher_id en legacy
    comercio_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # merchant_id en legacy
    bono_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    original_price = Column(Float, nullable=False)  # DECIMAL
    discount_price = Column(Float, nullable=False)  # DECIMAL
    discount_percentage = Column(Float, nullable=False)  # DECIMAL
    category = Column(String(100), nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    stock_total = Column(Integer, nullable=False)
    stock_available = Column(Integer, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Legacy
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=True)  # Legacy
    value = Column(Float, nullable=True)  # Legacy
    qr_code = Column(String(255), nullable=True)  # Legacy - ahora en BONO_CODES
    status = Column(String(50), nullable=True)  # Legacy - ahora en BONO_CODES
    expires_at = Column(Date, nullable=True)  # Legacy - use valid_until

    # Relationships
    comercio = relationship("User", foreign_keys=[comercio_id], back_populates="bonos")
    images = relationship("BonoImage", back_populates="bono")
    purchases = relationship("BonoPurchase", back_populates="bono")
    
    # Legacy relationships
    # merchant relationship removed - vouchers relationship doesn't exist in User model
    transaction = relationship("Transaction", back_populates="voucher", uselist=False)  # Legacy
    sales_commissions = relationship("SalesCommission", back_populates="voucher")  # Legacy

# Legacy alias
Voucher = Bono
VoucherStatus = None  # Deprecated - use redemption_status in BonoCode

