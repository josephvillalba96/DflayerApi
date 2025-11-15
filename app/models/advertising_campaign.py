"""
Campaign Model (CAMPAIGNS)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class BudgetType(str, enum.Enum):
    """Enum for budget types"""
    ADVERTISING = "advertising"
    SALES_COMMISSION = "sales_commission"


class CampaignStatus(str, enum.Enum):
    """Enum for campaign status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AdvertisingCampaign(Base):
    """Campaign model (CAMPAIGNS)"""
    __tablename__ = "campaigns"  # advertising_campaigns en legacy

    campaign_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # comercio que crea la campaña
    campaign_name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    total_budget = Column(Float, nullable=False)  # DECIMAL
    remaining_budget = Column(Float, nullable=False)  # DECIMAL
    budget_type = Column(SQLEnum(BudgetType), nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    merchant_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Legacy
    budget = Column(Float, nullable=True)  # Legacy - use total_budget

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="campaigns")
    campaign_posts = relationship("CampaignPost", back_populates="campaign")
    action_rewards = relationship("ActionReward", back_populates="campaign")
    segmentation = relationship("CampaignSegmentation", back_populates="campaign", uselist=False)
    interactions = relationship("Interaction", back_populates="campaign")
    sales_commissions = relationship("SalesCommission", back_populates="campaign")
    
    # Legacy relationships
    merchant = relationship("User", foreign_keys=[merchant_id], back_populates="campaigns_legacy")  # Legacy


class CommissionStatus(str, enum.Enum):
    """Enum for commission status"""
    PENDING = "pending"
    DISTRIBUTED = "distributed"
    FAILED = "failed"


class SalesCommission(Base):
    """Sales commission model (SALES_COMMISSIONS)"""
    __tablename__ = "sales_commissions"

    commission_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("bono_purchases.purchase_id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=True)
    total_commission_amount = Column(Float, nullable=False)  # DECIMAL
    platform_amount = Column(Float, nullable=False)  # DECIMAL - 50%
    users_amount = Column(Float, nullable=False)  # DECIMAL - 50%
    commission_status = Column(SQLEnum(CommissionStatus), default=CommissionStatus.PENDING)
    created_at = Column(Date, default=datetime.utcnow)
    distributed_at = Column(Date, nullable=True)
    
    # Legacy fields (kept for compatibility)
    voucher_id = Column(Integer, ForeignKey("bonos.bono_id"), nullable=True)  # Legacy
    commission_amount = Column(Float, nullable=True)  # Legacy - use total_commission_amount
    distributed = Column(Boolean, default=False)  # Legacy - use commission_status
    calculated_at = Column(Date, nullable=True)  # Legacy - use created_at

    # Relationships
    purchase = relationship("BonoPurchase", back_populates="sales_commissions")
    campaign = relationship("AdvertisingCampaign", back_populates="sales_commissions")
    commission_distributions = relationship("CommissionDistribution", back_populates="commission")
    
    # Legacy relationships
    voucher = relationship("Bono", foreign_keys=[voucher_id], back_populates="sales_commissions")  # Legacy

