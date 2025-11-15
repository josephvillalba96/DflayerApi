"""
Withdrawal Request Model (WITHDRAWAL_REQUESTS)
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class WithdrawalMethod(str, enum.Enum):
    """Enum for withdrawal methods"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    OTROS = "otros"


class RequestStatus(str, enum.Enum):
    """Enum for request status"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class WithdrawalRequest(Base):
    """Withdrawal request model (WITHDRAWAL_REQUESTS)"""
    __tablename__ = "withdrawal_requests"

    withdrawal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id"), nullable=False)
    amount = Column(Float, nullable=False)  # DECIMAL
    withdrawal_method = Column(SQLEnum(WithdrawalMethod), nullable=False)
    bank_account_id = Column(Integer, ForeignKey("tax_data.tax_data_id"), nullable=True)  # FK → FISCAL_DATA
    request_status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING)
    requested_at = Column(Date, default=datetime.utcnow)
    processed_at = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="withdrawal_requests")
    wallet = relationship("Wallet", back_populates="withdrawal_requests")
    bank_account = relationship("TaxData", foreign_keys=[bank_account_id])
    transaction = relationship("Transaction", back_populates="withdrawal_requests")

