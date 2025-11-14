"""
Advertising Campaign Model
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class AdvertisingCampaign(Base):
    """Advertising campaign model"""
    __tablename__ = "advertising_campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    budget = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    # Relationship with Merchant
    merchant = relationship("User", back_populates="campaigns")


class SalesCommission(Base):
    """Voucher sale commission model"""
    __tablename__ = "sales_commissions"

    commission_id = Column(Integer, primary_key=True, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.voucher_id"), nullable=False)
    commission_amount = Column(Float, nullable=False)
    distributed = Column(Boolean, default=False)
    calculated_at = Column(Date, default=datetime.utcnow)

    # Relationship with Voucher
    voucher = relationship("Voucher", back_populates="sales_commissions")

