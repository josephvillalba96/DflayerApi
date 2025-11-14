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
    VOUCHER_PURCHASE = "voucher_purchase"
    WITHDRAWAL = "withdrawal"
    ACTION_PAYMENT = "action_payment"


class TransactionStatus(str, enum.Enum):
    """Enum for transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Transaction(Base):
    """Financial transaction model"""
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=datetime.utcnow)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)

    # Relationship with User
    user = relationship("User", back_populates="transactions")
    
    # Relationship with Voucher (for voucher purchases)
    voucher = relationship("Voucher", back_populates="transaction", uselist=False)

