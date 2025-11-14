"""
Voucher Model
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class VoucherStatus(str, enum.Enum):
    """Enum for voucher status"""
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"


class Voucher(Base):
    """Digital voucher model"""
    __tablename__ = "vouchers"

    voucher_id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=True, unique=True)
    value = Column(Float, nullable=False)
    qr_code = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(VoucherStatus), default=VoucherStatus.ACTIVE)
    created_at = Column(Date, default=datetime.utcnow)
    expires_at = Column(Date, nullable=True)

    # Relationships
    merchant = relationship("User", back_populates="vouchers")
    transaction = relationship("Transaction", back_populates="voucher", uselist=False)
    sales_commissions = relationship("SalesCommission", back_populates="voucher")

