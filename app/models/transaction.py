"""
Transaction Model
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class TransactionType(str, enum.Enum):
    """Enum for transaction types"""
    EARNING = "earning"
    WITHDRAWAL = "withdrawal"
    PURCHASE = "purchase"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    # Legacy
    VOUCHER_PURCHASE = "voucher_purchase"  # Legacy - use PURCHASE
    ACTION_PAYMENT = "action_payment"  # Legacy - use EARNING


class TransactionStatus(str, enum.Enum):
    """Enum for transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    # Legacy
    REJECTED = "rejected"  # Legacy - use FAILED


class Transaction(Base):
    """Financial transaction model (TRANSACTIONS)"""
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # DECIMAL
    balance_before = Column(Float, nullable=False)  # DECIMAL
    balance_after = Column(Float, nullable=False)  # DECIMAL
    description = Column(String(500), nullable=True)
    reference_id = Column(String(255), nullable=True)  # VARCHAR - ID de la entidad relacionada
    reference_type = Column(String(100), nullable=True)  # VARCHAR - tipo de entidad relacionada
    transaction_status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(Date, default=datetime.utcnow)
    completed_at = Column(Date, nullable=True)
    
    # Legacy fields (kept for compatibility)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Legacy
    date = Column(Date, nullable=True)  # Legacy - use created_at
    status = Column(SQLEnum(TransactionStatus), nullable=True)  # Legacy - use transaction_status

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    
    # Legacy relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")  # Legacy
    voucher = relationship("Bono", foreign_keys="Bono.transaction_id", back_populates="transaction", uselist=False)  # Legacy: Voucher is alias
    
    # New relationships
    withdrawal_requests = relationship("WithdrawalRequest", back_populates="transaction")
    tax_records = relationship("TaxRecord", back_populates="transaction")

