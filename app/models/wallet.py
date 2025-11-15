"""
Wallet Model
User wallet for managing balances
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Wallet(Base):
    """User wallet model"""
    __tablename__ = "wallet"

    wallet_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    
    # Balance fields
    available_balance = Column(Float, default=0.0)  # Available to withdraw
    pending_balance = Column(Float, default=0.0)  # Pending validation
    total_earned = Column(Float, default=0.0)  # Total lifetime earnings
    total_withdrawn = Column(Float, default=0.0)  # Total lifetime withdrawals
    
    last_transaction_at = Column(Date, nullable=True)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wallet", uselist=False)
    transactions = relationship("Transaction", back_populates="wallet")
    withdrawal_requests = relationship("WithdrawalRequest", back_populates="wallet")

