"""
Commission Distribution Model (COMMISSION_DISTRIBUTIONS)
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from app.models.payment_distribution import DistributionStatus


class CommissionDistribution(Base):
    """Commission distribution model (COMMISSION_DISTRIBUTIONS)"""
    __tablename__ = "commission_distributions"

    distribution_id = Column(Integer, primary_key=True, index=True)
    commission_id = Column(Integer, ForeignKey("sales_commissions.commission_id"), nullable=False)
    beneficiary_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    level = Column(Integer, nullable=False)  # 1 a 5
    amount = Column(Float, nullable=False)  # DECIMAL
    distribution_status = Column(SQLEnum(DistributionStatus), default=DistributionStatus.PENDING)
    processed_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationships
    commission = relationship("SalesCommission", back_populates="commission_distributions")
    beneficiary_user = relationship("User", back_populates="commission_distributions_received")

